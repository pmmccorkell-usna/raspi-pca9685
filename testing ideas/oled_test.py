# Patrick McCorkell
# June 2021
# US Naval Academy
# Robotics and Control TSD
#

from time import sleep
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
from adafruit_ssd1306 import SSD1306_I2C
from sense_hat import SenseHat



class OLED:
	def __init__(self):
		# Instantiate i2c bus.
		i2c = busio.I2C(SCL, SDA)

		# Instantiate ssd1306 class over i2c.
		# Class(Width, Height, bus)
		self.oled = SSD1306_I2C(128, 32, i2c)
		self.clear_oled()
	
		# Instantiate an image the size of the screen
		self.image = Image.new("1", (self.oled.width, self.oled.height))

		# Instantiate an object to draw on the image.
		self.draw = ImageDraw.Draw(self.image)

		# Instantiate default font.
		self.font = ImageFont.load_default()

		# Instantiate Pi SenseHat.
		# self.sense = SenseHat()

		# Instantiate the joystick on Pi SenseHat
		# self.dpad = sense.stick

	def clear_oled(self):
		# Clear and show display.
		self.oled.fill(0)
		self.oled.show()

	def clear_draw(self):
		# Draw a black rectangle from edge to edge.
		self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)

	def get_IP(self):
		return subprocess.check_output("hostname -I | cut -d' ' -f1",shell=True).decode("utf-8")

	def get_CPU(self):
		return subprocess.check_output('cut -f 1 -d " " /proc/loadavg',shell=True).decode("utf-8")

	def update_stats(self,last_joystick):
		top = -2
		padding = 8
		x = 0

		self.clear_draw()
		dataframe = {
			'IP':self.get_IP(),
			'CPU':self.get_CPU(),
			'dpad':last_joystick
		}
		for index,key in enumerate(dataframe):
			textline = key + ": " + dataframe[key]
			self.draw.text((0,top+(index*padding)), textline,font=self.font,fill=255)
		self.oled.image(self.image)
		self.oled.show()



class Joystick:
	def __init__(self,display):
		self.disp = display
		self.sense = SenseHat()
		self.dpad = self.sense.stick

		self.released_val = self.get_ord('released')
		self.held_val = self.get_ord('held')
		self.pressed_val = self.get_ord('pressed')

		self.MIDDLE, self.DOWN, self.LEFT, self.RIGHT, self.UPLEFT, self.UPRIGHT, self.DOWNLEFT, self.DOWNRIGHT = 0,0,0,0,0,0,0,0
		self.UP = 0

		self.values = {
			'up':0,
			'down':0,
			'left':0,
			'right':0,
			# 'upleft':0,
			# 'upright':0,
			# 'downleft':0,
			# 'downright':0,
			'middle':0
		}

		self.diags = {
			'upleft':0,
			'upright':0,
			'downleft':0,
			'downright':0
		}

		# self.dpad.direction_right = self.detected_right
		# self.dpad.direction_left = self.detected_left
		# self.dpad.direction_up = self.detected_up
		# self.dpad.direction_down = self.detected_down
		# self.dpad.direction_middle = self.detected_middle

		self.dpad.direction_any = self.detected

		self.last_event = 'N/A'

		self.event_queue=[]

	def get_ord(self,some_string):
		returnval = 0
		for character in some_string:
			returnval += ord(character)
		return returnval

	def close(self):
		self.dpad.close()

	def setup_diags():
		dpad.direction_up = detect_up
		dpad.direction_down = detect_down

	def detected_left(self,event):
		check_val = self.get_ord(event.action)
		check_released = bool(check_val - self.released_val)
		check_hold = bool(check_val - self.held_val)
		self.LEFT = 1 * check_released
		self.last_event = event.direction
		self.event_queue.append(check_released * check_hold * event.direction)
		# if check_val:
		# 	self.last_event = event.direction
		# 	self.disp.update_stats(event.direction)

	def detected_right(self,event):
		check_val = self.get_ord(event.action)
		check_released = bool(check_val - self.released_val)
		check_hold = bool(check_val - self.held_val)
		self.RIGHT = 1 * check_released
		self.last_event = event.direction
		# self.event_queue.append(check_released * check_hold * event.direction)
		# if check_val:
		# 	self.last_event = event.direction
		# 	self.disp.update_stats(event.direction)

	def detected_up(self,event):
		check_val = self.get_ord(event.action)
		check_released = bool(check_val - self.released_val)
		check_hold = bool(check_val - self.held_val)
		if check_released:
			self.UP = 1
		else:
			self.UP = 0
		# self.UP = 1 * check_released
		self.last_event = event.direction
		# self.event_queue.append(check_released * check_hold * event.direction)
		self.UPLEFT = self.UP * self.LEFT
		self.UPRIGHT = self.UP * self.RIGHT
		# if check_val:
		# 	self.last_event = event.direction
		# 	self.disp.update_stats(event.direction)

	def detected_down(self,event):
		check_val = self.get_ord(event.action)
		check_released = bool(check_val - self.released_val)
		check_hold = bool(check_val - self.held_val)
		self.DOWN = 1 * check_released
		self.last_event = event.direction
		self.DOWNLEFT = self.DOWN * self.LEFT
		self.DOWNRIGHT = self.DOWN * self.RIGHT
		# self.event_queue.append(check_released * check_hold * event.direction)
		# if check_val:
		# 	self.last_event = event.direction
		# 	self.disp.update_stats(event.direction)

	def detected_middle(self,event):
		check_val = self.get_ord(event.action)
		check_released = bool(check_val - self.released_val)
		check_hold = bool(check_val - self.held_val)
		self.MIDDLE = 1 * check_released
		self.last_event = event.direction
		# self.event_queue.append(check_released * check_hold * event.direction)
			# self.disp.update_stats(event.direction)

	def detected(self,event):
		if not (event.action.find('released')):
			self.values[event.direction] = 0
		elif not (event.action.find('pressed')):
			self.values[event.direction] = 1
			self.last_event = event.direction
			self.event_queue.append(event.direction)
			self.update_display()
	
	def update_display(self):
		while(self.event_queue):
			oled.update_stats(self.event_queue.pop(0))


oled = OLED()
dpad = Joystick(oled)

def update():
	events = dpad.dpad.get_events()
	for event in events:
		if event.action=="pressed":
			oled.update_stats(event.direction)
			print(event.direction+": "+event.action)
			if event.direction == "middle":
				return 0
	return 1


# if __name__ == '__main__':
# 	print("running as main")
# 	keep_running = 1
# 	while(keep_running):
# 		keep_running = update()
# 	dpad.close()

def update_state():
	# oled.update_stats(dpad.last_event)
	if dpad.UPLEFT:
		print("up left")
	if dpad.UPRIGHT:
		print("up right")
	if (dpad.MIDDLE):
		return 0
	return 1

if __name__ == '__main__':
	print("running as main")
	keep_running = 1
	while(keep_running):
		oled.update_stats(dpad.last_event)
		keep_running = update_state()
		sleep(0.5)
	dpad.close()
