
# Code Author: Patrick Woolard
# Email: Jwoolard@augusta.edu
# Tello Drone Python Documentation: https://djitellopy.readthedocs.io/en/latest/tello/
# Arduino Python Tutorial: https://realpython.com/arduino-python/#:~:text=Hello%2C%20World!%E2%80%9D%20program.-,Uploading%20the%20Firmata%20Sketch,-Before%20you%20write

# Module Imports
import pyfirmata
import time
from djitellopy import Tello
import sys
import cv2
import threading



'''
This controller is for circuits designed with only push button inputs for drone control
'''
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



'''
This controller is for circuits designed with joystick inputs for drone control
'''
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
	
	board.analog[0].enable_reporting() # x val (Joystick 1)
	board.analog[1].enable_reporting() # y val (Joystick 1)

	board.analog[2].enable_reporting() # x val (Joystick 2)
	board.analog[3].enable_reporting() # y val (Joystick 2)

	print("Currently awaiting takeoff. (Press both buttons)")

	# Start thread to handle camera and drone battery display
	threading.Thread(target=Tello_Vision, args=(tello,board,), daemon=True).start() 

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
	
	up_down_speed = 0
	while True :
		pb1 = board.digital[2].read()
		pb2 = board.digital[3].read()
		
		x_val1 = board.analog[0].read() 
		y_val1 = board.analog[1].read()
		x_val2 = board.analog[2].read()
		y_val2 = board.analog[3].read()

		# For testing purposes (comment out as needed)
		# print(f"x val: {x_val1}")
		# print(f"y val: {y_val1}")
		# print()

		## JOYSTICK RULES W/ WIRES ON LEFT ##
		# CENTER/NO INPUT: Y = .50 X = .50
		# UP : Y = 0 X = .50
		# DOWN: Y = 1 X = .50
		# LEFT: Y = .50 X = 0
		# RIGHT: Y = .50 X = 1

		x_num = -1 * Normalize_JS(x_val1,speed) # -1 * when the drone is facing away
		y_num = Normalize_JS(y_val1,speed)
		yaw_speed = Normalize_JS(x_val2,speed)
		up_down_speed = Normalize_JS(y_val2,speed)


		# For testing purposes (comment out as needed)
		# if y_val is not None and x_val is not None: 
		# 	print(f"x_num: {x_num}")
		# 	print(f"y_num: {y_num}")
		# 	print()


		# input layout is more or less arbitrary. Change as desired...
		if pb1 and pb2:
			print("Drone is now landing")
			board.digital[7].write(0)
			tello.land()
			break
		elif pb1: # move drone up
			#up_down_speed = speed
			tello.send_command_without_return("flip f")
		elif pb2: # move drone down
			#up_down_speed = -speed
			tello.send_command_without_return("flip b")

		# Send the actual flight command
		tello.send_rc_control(x_num, y_num, up_down_speed, yaw_speed)

		time.sleep(0.01)



'''
This function is spun off as its own thread in order to see what the tello drone sees.
Camera frame errors may show in terminal due to missing some inital frames, but they can be ignored.
'''
def Tello_Vision(tello,board):
	tello.streamon()
	cap = tello.get_frame_read()

	# Current design is too account for inital takeoff double press.
	# This is sloppy and should be changed by a dedicated button or I/O later.
	while True:
		pb1 = board.digital[2].read()
		pb2 = board.digital[3].read()
		cv2.waitKey(1)
		image = cap.frame
		try:
			battery_status = tello.get_battery()
		except:
			battery_status = -1
		cv2.putText(image, "Battery: {}".format(battery_status), (5, 720 - 5), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
		cv2.imshow('Tello-Vision', image)
		if pb1 and pb2:
			break

	time.sleep(2) # gives you some time to take hands off of landing buttons

	while True:
		pb1 = board.digital[2].read()
		pb2 = board.digital[3].read()
		cv2.waitKey(1)
		image = cap.frame
		try:
			battery_status = tello.get_battery() 
		except:
			battery_status = -1
		cv2.putText(image, "Battery: {}".format(battery_status), (5, 720 - 5), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
		cv2.imshow('Tello-Vision', image)
		if pb1 and pb2:
			break

	cv2.destroyAllWindows()



'''
This function takes maps the analog inputs of the joysticks and normalizes them to speeds for the tello rc_speed function.
'''
def Normalize_JS(val,speed):
	# Normalize joystick input relative to desired direction 
		if val is not None:
			#### X OR Y AXIS ####
			if val < .50: # MOVE FORWARD (Ex: I want to move forward w/ speed of +30)
				# Ex: y_val = .35
				num = val * 200 # y_num = 70
				num = int(100 - num) # y_num = 30
			elif val >= .50: # MOVE BACK (Ex: I want to move back w/ speed of -30)
				# Ex: y_val = .65
				num = val - .5  # y_num = .15
				num = -1* int(num * 200) # y_num = -30
			
			# Handle min-max speed conditions
			if abs(num) < 10:
				num = 0
			elif abs(num) > speed:
				if num < 0: 
					num = -speed
				else:
					num = speed
		
		else:
			num = 0

		
		return num



##### Main #####

if "-BB" in sys.argv:
	BB_Controller()
else:
	JS_Controller()

