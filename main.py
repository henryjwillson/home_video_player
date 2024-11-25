# This is a test file to understand movie playback commands
from tkinter import *
import os
from os import listdir
import subprocess
from multiprocessing import Process
import time
import random
from pynput.keyboard import Key, Controller
from pynput import keyboard
from gpiozero import Button, LED
import _thread
import datetime


def day_time_checker(morning_time, first_morning_trigger, evening_time):
	while True:
		time.sleep(360)
		current_time = datetime.datetime.now().time()
		print(current_time)
		if current_time > morning_time and current_time < first_morning_trigger:
			screen_power.manual_pause = False
		elif current_time > morning_time or current_time < evening_time:
			print("Day time operation, motion sensor enabled")
		else:
			print("Night time operation, motion sensor disabled")
			screen_power.manual_pause = True

morning_time = datetime.time(6,0,0,0)
first_morning_trigger = datetime.time(6,20,0,0)
evening_time = datetime.time(22,0,0,0)
#day_time_checker(morning_time, evening_time)
print(morning_time, first_morning_trigger, evening_time)

time.sleep(1)

class screen_condition():
	
	def __init__(self, value, standby_timer, manual_pause):
		self.value = value
		self.standby_timer = standby_timer
		self.manual_pause = manual_pause
		
screen_power = screen_condition("on", 40, False)


movie_list = listdir("/home/pi/Documents")

RE_button_A = Button(18)
RE_button_B = Button (23)
Screen_power_trigger = LED(27)
Screen_power_button = Button(12)
PIR_Sensor = Button(17)
next_video_button = Button(24)


old_a = True
old_b = True

max_vol = 9
min_vol = -60

def manual_on():
	time.sleep(3600)
	screen_power.manual_pause = False


def get_power_press():
	while True:
		time.sleep(1)
		val = str(Screen_power_button.value)
		if val == "0":
			time.sleep(0.25)
			val = str(Screen_power_button.value)
			if val == "0":
				time.sleep(0.25)
				val = str(Screen_power_button.value)
				if val == "0":
					time.sleep(0.25)
					val = str(Screen_power_button.value)
					if val == "0":
						print("Screen_power_button pressed")
						print(Screen_power_button.value)
						Screen_power_trigger.on()
						time.sleep(0.25)
						Screen_power_trigger.off()
						if screen_power.value == "on":
							screen_power.value = "off"
							screen_power.manual_pause = True
							_thread.start_new_thread(manual_on,())
						else:
							screen_power.value = "on"
						time.sleep(1)
		

def motion_sensor():
	timer_count = 0
	while True:
		time.sleep(1)
		sens = str(PIR_Sensor.value)
		if sens == "0":
			print("Motion_detected")
			timer_count = 0
			if screen_power.value == "off" and screen_power.manual_pause == False:
				time.sleep(1)
				sens = str(PIR_Sensor.value)
				if sens == "0":
					print("Motion_detected twice")
					time.sleep(1)
					sens = str(PIR_Sensor.value)
					if sens == "0":
						print("Motion_detected three times")
						time.sleep(0.25)
						sens = str(PIR_Sensor.value)
						if sens == "0":
							print("Motion_detected four times")
							time.sleep(0.25)
							sens = str(PIR_Sensor.value)
							if sens == "0":
								print("Motion_detected five times")
								timer_count = 0
								if screen_power.value == "off" and screen_power.manual_pause == False:
									print("Turning screen back on motion triggered")
									Screen_power_trigger.on()
									time.sleep(0.25)
									Screen_power_trigger.off()
									screen_power.value = "on"
		else:
			timer_count += 1
			print("timer_count is: ",timer_count)
			if timer_count >= screen_power.standby_timer:
				print("standby timer reached")
				if screen_power.value == "on":
					print("Stanby reached, turning screen off")
					Screen_power_trigger.on()
					time.sleep(0.25)
					Screen_power_trigger.off()
					screen_power.value = "off"

class speaker_volume():
	
	def __init__(self, value):
		self.value = value
		
def get_encoder_turn():
	# return -1 (ccw), 0 (no-movement), +1 (cw)
	global old_a, old_b
	result = 0
	new_a = RE_button_A.is_pressed
	new_b = RE_button_B.is_pressed
	if new_a != old_a or new_b != old_b:
		if old_a == 0 and new_a == 1:
			print("left")
			result = (old_b * 2 - 1)
		elif old_b == 0 and new_b == 1:
			print("right")
			result = -(old_a * 2 - 1)
	old_a, old_b = new_a, new_b
	time.sleep(0.001)
	return result
	
def volume_control():
	while True:
		change = get_encoder_turn()
		if change != 0:
			print(change)
			if change > 0 and volume.value <= max_vol:
				volume.value = volume.value + (3 * change)
				if change > 0:
					keyboard.press('+')
					time.sleep(0.25)
					keyboard.release('+')
					time.sleep(0.25)
			else:
				if volume.value >= min_vol:
					volume.value = volume.value + (3 * change)
					keyboard.press('-')
					time.sleep(0.25)
					keyboard.release('-')
					time.sleep(0.25)
					
			print(volume.value)

print(movie_list)
print("This is the movie list above....")
#time.sleep(10)

#Slicing list of files to only include mp4 files
for item in movie_list:
	if item[-2:] != "pg":
		movie_list.remove(item)
		print("I found the mpg file...", item)
		
print(movie_list)

def next_movie(key):
	if key == Key.enter:		
		p.terminate()
		keyboard.press(Key.esc)
		keyboard.release(Key.esc)
		print("escape button simulated")


listener = keyboard.Listener(on_press = next_movie, on_release = next_movie)
listener.start()
keyboard = Controller()

cwd_retrieve = os.getcwd()


def blackbackground():
	root = Tk()
	root.geometry('1024x600+0+0')
	root.title('App Window')
	root.attributes('-type', 'dock')
	pane = Frame(root, bg="black")
	pane.pack(fill = BOTH, expand = True)
	root.mainloop()

def launch_mp4(name):
	print(name)
	subprocess.run(["omxplayer -o both 422sBand2009.mpg"], cwd=cwd_retrieve, shell=True)
	
#-b --blank	

volume = speaker_volume(0)

def launch_mp4_list(name):
	print(name)
	print("current speaker volume for new video is: ", volume.value)
	string_vol = str(volume.value * 100)
	#"omxplayer -o both --win 0,0,1024,600 --aspect-mode letterbox --blank --alpha 250 --vol " + string_vol + " /home/pi/Documents/" + name
	launch_command = "omxplayer -o both --win 0,0,1024,600 --aspect-mode letterbox --blank --alpha 250 --vol " + string_vol + " /home/pi/Documents/" + name
	print(launch_command)
	subprocess.run([launch_command], cwd=cwd_retrieve, shell=True)

#subprocess.run(["omxplayer -o both GOPR2039.MP4"], cwd=cwd_retrieve, shell=True)

#p = Process(target = launch_mp4, args = ("video",))
#p.start()


_thread.start_new_thread(blackbackground,())
_thread.start_new_thread(get_power_press,())
_thread.start_new_thread(motion_sensor,())
_thread.start_new_thread(volume_control,())
_thread.start_new_thread(day_time_checker,(morning_time, first_morning_trigger, evening_time))
time.sleep(0.25)


#volume_control(volume)

while True:
	random.shuffle(movie_list)
	for movie in movie_list:
		#_thread.start_new_thread(volume_control,())
		p = Process(target = launch_mp4_list, args = (movie,))
		p.start()
		video_still_playing = p.is_alive()
		while video_still_playing == True:
			video_still_playing = p.is_alive()
			time.sleep(0.25)
			if str(next_video_button.value) == "1":
				print("Next video button is pressed")
				p.terminate()
				keyboard.press(Key.esc)
				time.sleep(0.1)
				keyboard.release(Key.esc)
			if video_still_playing == False:
				print("video is no longer playing")
		print("movie completed")
	print("all movies completed, starting again")


p = Process(target = launch_mp4_list, args = (movie_list[1],))
p.start()
time.sleep(4)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
keyboard.press('-')
keyboard.release('-')
time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
# keyboard.press('+')
# keyboard.release('+')
# time.sleep(0.5)
keyboard.press(Key.esc)
keyboard.release(Key.esc)
print("escape button simulated")

random.shuffle(movie_list)
p = Process(target = launch_mp4_list, args = (movie_list[1],))
p.start()

time.sleep(4)
keyboard.press(Key.esc)
keyboard.release(Key.esc)

random.shuffle(movie_list)
p = Process(target = launch_mp4_list, args = (movie_list[1],))
p.start()
time.sleep(2)
print("terminating...)")

print("keyboard presses complete")
#p4 = subprocess.run(["omxplayer -b --vol -1000"])

while True:
	for movie in movie_list:
		p = Process(target = launch_mp4_list, args = (movie,))
		p.start()
		p.join()	
