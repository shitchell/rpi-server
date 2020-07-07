import os
import time
import pigpio

NUM_GPIO = 17
STATE_FILEPATH = "/tmp/projector.state"
LOCK_FILEPATH = "/tmp/projector.lock"

def get_state(filepath=STATE_FILEPATH):
	if not os.path.exists(filepath):
		set_state("down")
	return open(filepath).read()

def set_state(state, filepath=STATE_FILEPATH):
	f = open(filepath, "w")
	f.write(state)
	f.close()

def get_lock(filepath=LOCK_FILEPATH):
	if not os.path.exists(filepath):
		open(filepath, 'a').close()
		return True
	return False

def release_lock(filepath=LOCK_FILEPATH):
	if os.path.isfile(filepath):
		os.remove(filepath)
		return True
	return False

def set_pulsewidth(width):
	pi = pigpio.pi()
	pi.set_servo_pulsewidth(NUM_GPIO, width)

def do_up(req, *args, **kwargs):
	'''Roll the projector screen up'''
	if get_state() == "up":
		return False
	get_lock()
	set_pulsewidth(2500)
	time.sleep(11.8)
	set_pulsewidth(0)
	time.sleep(1)
	set_state("up")
	release_lock()

def do_down(req, *args, **kwargs):
	'''Roll the projector screen down'''
	if get_state() == "down":
		return False
	get_lock()
	set_pulsewidth(500)
	time.sleep(10.40)
	set_pulsewidth(0)
	time.sleep(1)
	set_state("down")
	release_lock()

def do_toggle(req, *args, **kwargs):
	'''Toggle the projector screen state'''
	if get_state() == 'down':
		do_up(req, *args, **kwargs)
	else:
		do_down(req, *args, **kwargs)

def do_stop(req, *args, **kwargs):
	'''Stop the projector screen'''
	set_pulsewidth(0)
