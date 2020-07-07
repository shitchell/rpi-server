import os
import sys
import random
import subprocess
import serve

playlist_path = serve.SCRIPT_DIRPATH + "local.txt"
fifo_path = "/tmp/rpi_omx"
default_volume = "-2000"

# Make sure that omxplayer is installed
cmd = subprocess.Popen(["which", "omxplayer"], stdout=subprocess.PIPE)
if not cmd.stdout.read():
	raise Exception("This module requires 'omxplayer' to be installed")

# Make sure we have a fifo for omxplayer
def create_fifo():
	global fifo_path
	# Delete a previous fifo if it exists
	if os.path.exists(fifo_path):
		remove_fifo()
	# Create a new fifo and append a new number if the filename already exists
	fifo_created = False
	i = 0
	while not fifo_created:
		fifo_path = fifo_path + ("-%i" % i if i else "")
		try:
			os.mkfifo(fifo_path)
		except OSError:
			print("! Failed to create fifo '%s'" % fifo_path)
		else:
			fifo_created = True
		i += 1

def write_to_fifo(text):
	global fifo_path
	if os.path.exists(fifo_path):
		f = open(fifo_path, 'w')
		f.write(text + "\n")
		f.close()
	else:
		print("! No fifo to write to")

def remove_fifo():
	global fifo_path
	os.remove(fifo_path)

def get_videos():
	global playlist_path
	
	# Load video information from a file
	# file follows the format 'Artist\tSong\tTags\tFilepath'
	f = open(playlist_path)
	data = f.read()
	f.close()
	
	# Parse the video information
	videos = dict()
	data = data.split('\n')
	for datum in data:
		line = datum.split("#")[0]
		if line:
			fields = line.split('\t')
			if len(fields) == 4:
				artist, song, path, tags = fields
				tags = tags.split(',')
				videos[path] = {"artist": artist, "title": song, "tags": tags}
	return videos

def play(filepath, **kwargs):
	global fifo_path
	# Check if a fifo exists
	if os.path.exists(fifo_path):
		write_to_fifo("q")
	else:
		create_fifo()
	fifo_stdin = open(fifo_path, "r")
	# convert kwargs into command line options
	for kwarg in kwargs:
		opts = ["%s %s" % (i[0], i[1]) for i in kwargs.items()]
	command = ["omxplayer", filepath] + opts
	subprocess.Popen(command, stdin=fifo_stdin)

def do_play(req, *args, **kwargs):
	'''Play a file'''
	if args:
		filepath = args[0]
		play(filepath, **kwargs)

def do_stop(req, *args, **kwargs):
	'''Stop omxplayer playback'''
	write_to_fifo("q")

def do_plause(req, *args, **kwargs):
	'''Toggle omxplayer play/pause status'''
	write_to_fifo("p")

def do_vol(req, *args, **kwargs):
	'''Control the volume of a currently playing song'''
	if args:
		arg = args[0]
		if arg == "up":
			write_to_fifo("+")
		elif arg == "down":
			write_to_fifo("-")
do_vol.samples = [
	"omx.vol/up",
	"omx.vol/down"
]

def do_random(req, *args, **kwargs):
	'''Play a random file from a local playlist'''
	global playlist_path
	
	if args:
		subaction = args[0]
		# Go through the available actions
		if subaction == "list":
			f = open(playlist_path, 'r')
			data = f.read()
			f.close()
			req.wfile.write(bytes("<pre>%s</pre>" % data, "UTF-8"))
	else:
		filepath = random.choice(list(get_videos().keys()))
		play(filepath)
do_random.samples = [
	"/omx.random",
	"/omx.random/list",
#	"/omx.random?tag=acoustic",
#	"/omx.random?band=Imagine%20Dragons"
]

def do_video(req, *args, **kwargs):
	'''Play a specific video from $HOME/Videos/'''
	
	if args:
		filename = args[0]
		filepath = os.path.expanduser("~/Videos/" + os.path.basename(filename))
		play(filepath)
	return True
do_video.samples = ["/omx.video/thinking.mp4"]
