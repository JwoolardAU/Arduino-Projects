
# Code Author: Patrick Woolard
# Email: Jwoolard@augusta.edu
# Tello Drone Python Documentation: https://djitellopy.readthedocs.io/en/latest/tello/
# Arduino Python Tutorial: https://realpython.com/arduino-python/#:~:text=Hello%2C%20World!%E2%80%9D%20program.-,Uploading%20the%20Firmata%20Sketch,-Before%20you%20write

# Module Imports
import pyfirmata
import time
from djitellopy import Tello
import sys

# This controller is for circuits designed with only push button inputs for drone control
def BB_Controller():

	# object instantiations
	tello = Tello()
	tello.connect()

	#board = pyfirmata.Arduino('/dev/ttyACM0') # Use this when on linux OS
	board = pyfirmata.Arduino('COM6') # Use this when on windows OS

	it = pyfirmata.util.Iterator(board)
	it.start()

	board.digital[2].mode = pyfirmata.INPUT
	board.digital[3].mode = pyfirmata.INPUT
	board.digital[4].mode = pyfirmata.INPUT
	board.digital[5].mode = pyfirmata.INPUT

	print("Currently awaiting takeoff. (Press both buttons)")


	# takeoff control loop
	while True:
		pb1 = board.digital[2].read()
		pb2 = board.digital[3].read()
		
		# input layout is more or less arbitrary. Change as desired...
		if pb1 and pb2:
			print("Drone is taking off. Remove hands from buttons.")
			tello.takeoff()
			board.digital[7].write(1) # while the drone is in flying command mode the led stays on
			break
		time.sleep(0.1)
		

	time.sleep(4) # gives you some time to take hands off of landing buttons

	# speed of drone (I believe it's in cm/s, check docs )
	try:
		speed = int(sys.argv[sys.argv.index('-spd')+1])		# You can feed speed as a command line arg (i.e. 'python .\Python_BB_Drone.py -spd 50' )
		if speed < 0 or speed > 100:
			print("Sorry, speed values must be between 0 and 100. Defaulting to 30.")
			raise
	except:
		speed = 30 # Default speed

	print("In command mode.")

	# movement/land control loop 
	while True:
		pb1 = board.digital[2].read()
		pb2 = board.digital[3].read()
		pb3 = board.digital[4].read()
		pb4 = board.digital[5].read()
		
		# input layout is more or less arbitrary. Change as desired...
		if pb1 and pb2:
			print("Drone is now landing")
			board.digital[7].write(0)
			tello.land()
			break
		elif pb1 and pb3:
			tello.send_rc_control(0, 0, speed, 0) # move up rc cmd
		elif pb2 and pb4:
			tello.send_rc_control(0, 0, -speed, 0) # move down rc cmd
		elif pb1:
			tello.send_rc_control(0, speed, 0, 0) # move forward rc cmd
		elif pb2:
			tello.send_rc_control(0, -speed, 0, 0) # move backward rc cmd
		elif pb3:
			tello.send_rc_control(speed, 0, 0, 0) # move right? rc cmd
		elif pb4:
			tello.send_rc_control(-speed, 0, 0, 0) # move left? rc cmd
		else:
			tello.send_rc_control(0, 0, 0, 0) # if no buttons are being pushed then the drone will do nothing/stop
		
		time.sleep(0.1)


# This controller is for circuits designed with joystick inputs for drone control
def JS_Controller():

	# object instantiations
	tello = Tello()
	tello.connect()

	#board = pyfirmata.Arduino('/dev/ttyACM0') # Use this when on linux OS
	board = pyfirmata.Arduino('COM6') # Use this when on windows OS

	it = pyfirmata.util.Iterator(board)
	it.start()

	board.digital[2].mode = pyfirmata.INPUT # PB 1
	board.digital[3].mode = pyfirmata.INPUT # PB 2
	
	board.analog[0].enable_reporting() # x val
	board.analog[1].enable_reporting() # y val

	print("Currently awaiting takeoff. (Press both buttons)")


	# takeoff control loop
	while True:
		pb1 = board.digital[2].read()
		pb2 = board.digital[3].read()
		
		# input layout is more or less arbitrary. Change as desired...
		if pb1 and pb2:
			print("Drone is taking off. Remove hands from buttons.")
			tello.takeoff()
			board.digital[7].write(1) # while the drone is in flying command mode the led stays on
			break
		time.sleep(0.1)

	time.sleep(2) # gives you some time to take hands off of landing buttons

	# maximum speed of drone (I believe it's in cm/s, check docs )
	try:
		speed = int(sys.argv[sys.argv.index('-spd')+1])		# You can feed speed as a command line arg (i.e. 'python .\Python_BB_Drone.py -spd 50' )
		if speed < 0 or speed > 100:
			print("Sorry, speed values must be between 0 and 100. Defaulting to 50.")
			raise
	except:
		speed = 50 # Default speed

	print("In command mode.")

	while True : 
		pb1 = board.digital[2].read()
		pb2 = board.digital[3].read()
		
		x_val = board.analog[0].read()
		y_val = board.analog[1].read()

		# For testing purposes (comment out as needed)
		# print(f"x val: {x_val}")
		# print(f"y val: {y_val}")
		# print()

		## JOYSTICK RULES W/ WIRES ON LEFT ##
		# CENTER/NO INPUT: Y = .50 X = .50
		# UP : Y = 0 X = .50
		# DOWN: Y = 1 X = .50
		# LEFT: Y = .50 X = 0
		# RIGHT: Y = .50 X = 1


		# Normalize joystick input relative to desired direction 
		if y_val is not None:
			#### Y AXIS ####
			if y_val < .50: # MOVE FORWARD (Ex: I want to move forward w/ speed of +30)
				# Ex: y_val = .35
				y_num = y_val * 200 # y_num = 70
				y_num = int(100 - y_num) # y_num = 30
			elif y_val >= .50: # MOVE BACK (Ex: I want to move back w/ speed of -30)
				# Ex: y_val = .65
				y_num = y_val - .5  # y_num = .15
				y_num = -1* int(y_num * 200) # y_num = -30
	
		if x_val is not None:
			#### X AXIS ####
			if x_val < .50: # MOVE LEFT (I want to move left w/ speed of -30)
				# Ex: x_val = .35
				x_num = x_val * 200 # x_num = 70
				x_num = -1 * int(100 - x_num) # x_num = 30
			elif x_val >= .50: # MOVE RIGHT (I want to move right w/ speed of +30)
				# Ex: y_val = .65
				x_num = x_val - .5  # x_num = .15
				x_num = int(x_num * 200) # x_num = -30
		

		# Handle min-max speed conditions
		if y_val is not None and x_val is not None:

			if abs(y_num) < 10:
				y_num = 0
			elif abs(y_num) > speed:
				if y_num < 0: 
					y_num = -speed
				else:
					y_num = speed

			if abs(x_num) < 10:
				x_num = 0
			elif abs(x_num) > speed:
				if x_num < 0: 
					x_num = -speed
				else:
					x_num = speed

		# For testing purposes (comment out as needed)
		# if y_val is not None and x_val is not None: 
		# 	print(f"x_num: {x_num}")
		# 	print(f"y_num: {y_num}")
		# 	print()

		tello.send_rc_control(x_num, y_num, 0, 0)

		# input layout is more or less arbitrary. Change as desired...
		if pb1 and pb2:
			print("Drone is now landing")
			board.digital[7].write(0)
			tello.land()
			break



		time.sleep(0.1)



##### Main #####

if "-BB" in sys.argv:
	BB_Controller(
else:
	JS_Controller()


