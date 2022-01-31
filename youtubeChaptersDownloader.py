

import pytube
import os
import json
import sys
import subprocess

#getting url, which can be passed as an argument to the script or inserted after starting the script
if(len(sys.argv) < 2):
	print("Please insert the video URL:\nps: you can also directly pass the link as a parameter of the script")
	url = input()
else:
	url = sys.argv[1]

#checking if ffmpeg is installed
if(subprocess.call(['which', 'ffmpeg']) != 0):
	print("Please install ffmpeg!")
	exit()

#defining functions and constants
PYTHONSCRIPTSUPPORTFILE = 'PYTHONSCRIPTSUPPORTFILE'

def getBestVideoStream(lista):
	ress = []
	for i in lista:
		if(i.resolution != None):
			ress.append(int(i.resolution[:-1]))
		else:
			ress.append(-1)
	return lista[ress.index(max(ress))]

def getStreamExtension(i):
	return i.mime_type.split('/')[1]

def getBestAudioStream(lista):
	ress = []
	for i in lista:
		if(i.type=="audio"):
			ress.append(int(i.abr[:-4]))
		else:
			ress.append(-1)
	return lista[ress.index(max(ress))]

print("Fetching video info...")
youtube = pytube.YouTube(url)

if(len(youtube.streams) == 0):
	print("Couldn't download video!")
	exit()


print("Finding best quality...")
video = getBestVideoStream(youtube.streams)
title = video.title.replace(":", "").replace(",", "")
videoExtension = getStreamExtension(video)
audio = getBestAudioStream(youtube.streams)
audioExtension = getStreamExtension(audio)

videoFilePath = title+'.'+videoExtension
audioFilePath = title+'.'+audioExtension

print("Found video: "+video.resolution+"@"+str(video.fps))
print("Found audio: "+str(audio.abr))

j = json.loads(os.popen('youtube-dl -j ' + url).read())
print("Downloading video...")
video.download()
print("Downloading audio...")
audio.download()

print("Resolving chapters")
if(j['chapters'] == None):
	print("Could find only one chapter in the video!")
	chaptersFound = False;
	
else:
	chaptersFound = True;

	chapters = j['chapters']
	fstr = ""
	for c in chapters:
		fstr = fstr + """[CHAPTER]
	TIMEBASE=1/10
	START="""+str(c['start_time']*10)+"""
	END="""+str(c['end_time']*10)+"""
	title="""+str(c['title'])+"""

	"""
	print("Found " + len(chapters) + " chapters")



print("Combining audio & video and burying chapters...")
with open(videoFilePath) as videoInputFile, open(audioFilePath) as audioInputFile:
	os.system('ffmpeg -i \"'+videoInputFile.name+'\" -f ffmetadata '+PYTHONSCRIPTSUPPORTFILE)

	if(chaptersFound):
		with open(PYTHONSCRIPTSUPPORTFILE, "a") as metadataFile:
			metadataFile.write(fstr)
			
	os.system('ffmpeg -i \"' + videoInputFile.name + '\" -i \"'+audioInputFile.name+'\" -i '+PYTHONSCRIPTSUPPORTFILE+' -map_metadata 1 -c:v copy -c:a aac \"'+title+'.mkv\"')


print("Finishing up")
os.remove(PYTHONSCRIPTSUPPORTFILE)
os.system('rm \"' + videoFilePath + "\"")
os.system('rm \"' + audioFilePath + "\"")
print("\n\nEverything done! Please check github.com/AlexPerathoner!")





