# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#

# import concurrent.futures
from threading import Thread
from multiporcessing import Process, Pipe
import surface
import xb
import mbed
from time import sleep, time
import atexit
from gc import trash
import mocap

qtm_server='192.168.5.4'   # IP of PC running QTM Motive

max_speed = 400   # us		speed limit

rigid_body_name = 'RED Dwarf'

class event_flags:
	def __init__(self):
		self.set_flag(1)

	def set_flag(self,val=None):
		if val is not None:
			self.run_flag = val
		return self.run_flag

pwm_flag = event_flags()
qtm_flag = event_flags()
xbox_flag = event_flags()
mbed_flag = event_flags()
plot_flag = event_flags()

pwm_interval = 0.02		# 20 ms
qtm_interval = 0.005	# 5 ms
xbox_interval = 0.01	# 10 ms
mbed_interval = 0.02	# 20 ms
plot_interval = .1		# 100 ms

measured_active = {
	'heading' : 0xffff
}

###############################################################
#################################################################

############ COME BACK TO THIS ONE ############
pwm = {
	##### Thruster Values ?? ####
}
def pwm_setup():
	global pwm_pipe_in
	pwm_pipe_in,pwm_pipe_out = Pipe()
	pwm_process = surface. #####################
	##############################################
	##############################################
	##############################################

# def pwm_process_thread( ... ARGS ...):
# 	global pwm, pwm_interval
# 	interval = pwm_interval


# 	#############
# 	# This part better in xbox process ?
# 	#############
# 	# for k in measured_active:
# 	# 	measured_active[k] = (qtm[k] * xbox['mode']) + (bno[k] * (not xbox['mode']))
# 	# print(measured_active)


# 	executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
# 	while(pwm_flag.set_flag()):
# 		start = time()

# 		################# CHECK THIS ####################
# 		##################################
# 		##############################
# 		# def process_commands():
# 		for k,v in incoming_commands:
# 			surface.issueCommand(k,v)
# 			# return surface.thrusters.update()

# 		############ COME BACK TO THIS ONE ############
# 		pwm_process = executor.submit(surface. ????, measured_active)
# 		surface.azThrusterLogic()
# 		###############################################

# 		pwm = pwm_process.result()
# 		sleeptime = max(interval + start - time(), 0.0)
# 		sleep(sleeptime)
# 	print("shutting down executor")
# 	executor.shutdown(wait=False,cancel_futures=True)


def xbox_setup():
	global xb_pipe_in,xbox_process,xbox_controller
	xb_pipe_in, xb_pipe_out = Pipe()
	xbox_controller = xb.XBoxController(xb_pipe_in)
	xbox_process = Process(target=xbox_controller.poll,daemon=True)
	xbox_process.start()

xbox = {
	'facing':999,
	'offset':999,
	'speed':999,
	'maintain':1,
	'mode':1,		# mode 1 qtm, mode 0 bno
	'quit':0
}
def xbox_read():
	global xbox_pipe_in, xbox
	read_pipe = xbox_pipe_in
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv()
	if buffer:
		xbox = buffer
def xbox_stream():
	global xbox
	interval = xbox_interval
	while(1):
		start = time()
		xbox_read()
		diff = interval+start-time()
		sleeptime=max(diff,0)
		sleep(sleeptime)
		# print('xbox: '+str(xbox))

# def xbox_process_thread():
# 	global xb, xbox_interval
# 	interval = xbox_interval
# 	executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
# 	xbox_buffer = xbox
# 	while(xbox_flag.set_flag()):
# 		start = time()
# 		incoming_commands = {}

# 		xbox_process = executor.submit(mbed.get_angles)
# 		xbox_buffer = xbox_process.result()


# 		# if xbox_buffer['mode'] = 1, use QTM MoCap data for control
# 		# if xbox_buffer['mode'] = 0, use BNO-055 IMU data for control
# 		for k in measured_active:
# 			measured_active[k] = (xbox_buffer['mode'] * qtm[k]) + ((not xbox_buffer['mode']) * bno[k])


# 		# Quit if quit signal is sent
# 		xbox_flag.set_flag(xbox_buffer['quit'])

# 		xbox = xbox_buffer

# 		sleeptime  = max(interval + start - time(), 0.0)
# 		sleep(sleeptime)
# 	print("shutting down executor")
# 	executor.shutdown(wait=False,cancel_futures=True)
# 	exit_program()



bno = {
	'heading':999,
	'roll':999,
	'pitch':999,
	'calibration':999,
	'status':999
}
def mbed_process_thread():
	global bno, mbed_interval
	interval = mbed_interval
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	while(mbed_flag.set_flag()):
		start = time()
		mbed_process = executor.submit(mbed.get_angles)
		bno = mbed_process.result()
		sleeptime = max(interval + start - time(), 0.0)
		sleep(sleeptime)
	print("shutting down executor")
	executor.shutdown(wait=False,cancel_futures=True)


def qtm_process_setup():
	global qualisys, qtm_server,qtm_pipe_in,mocap_process
	qtm_pipe_in, qtm_pipe_out = Pipe()
	qualisys = mocap.Motion_Capture(qtm_pipe_out,qtm_server)

	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	mocap_process = Process(target=qualisys.start,daemon=True)
	mocap_process.start()


qtm = {
			'index':0xffff,
			'x':999,
			'y':999,
			'z':999,
			'roll':999,
			'pitch':999,
			'heading':999
}
def qtm_read(name):
	global qtm_pipe_in, qtm
	read_pipe = qtm_pipe_in
	# name = rigid_body_name
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv().get(rigid_body_name)
	if buffer:
		qtm = buffer
def qtm_stream():
	global qtm, qtm_flag, rigid_body_name
	interval = 0.005
	r_name = rigid_body_name
	while(qtm_flag.set_flag()):
		start=time()
		qtm_read(r_name)
		diff = interval+start-time()
		sleeptime = max(diff, 0)
		sleep(sleeptime)
		# print(qtm)


def plotting():
	global bno,qtm,xbox,pwm,plotting_interval
	interval = plotting_interval
	while(plot_flag.set_flag()):
		start = time()

		############ GRAPH AND COMPARE THINGS ############


		sleeptime = max(interval + start - time(), 0.0)
	

def exit_program():
	global qtm
	print("exiting program")
	pwm_flag.set_flag(0)
	qtm_flag.set_flag(0)
	xbox_flag.set_flag(0)
	mbed_flag.set_flag(0)
	plot_flag.set_flag(0)

	qtm.connected.disconnect()

	print()
	print('Exiting Program.')
	print()

	xb.close()
	for i in range(3):
		surface.thrusters.exitProgram()
		print(f'STOPPING THRUSTERS: {i}')
		sleep(0.3)

	print()

atexit.register(exit_program)




def setup():
	surface.pwmControl.servoboard.set_max(max_speed/1.2)
	surface.stopAll()

	pwm_thread = Thread(target=pwm_process_thread,daemon=True)
	pwm_thread.start()

	qtm_process_setup()
	qtm_thread = Thread(target=qtm_stream,daemon=True)
	qtm_thread.start()

	xbox_thread = Thread(target=xbox_stream,daemon=True)
	xbox_thread.start()

	mbed_thread = Thread(target=mbed_process_thread,daemon=True)
	mbed_thread.start()

	plot_thread = Thread(target=plotting,daemon=True)
	plot_thread.start()


setup()
