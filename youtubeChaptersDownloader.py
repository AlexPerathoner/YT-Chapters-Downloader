

import pytube
import youtube_dl
import os
import json
import sys

#getting url, which can be passed as an argument to the script or inserted after starting the script
if(len(sys.argv) < 2):
	print("Insert url")
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

print("Finding best quality...")
video = getBestVideoStream(youtube.streams)
videoExtension = getStreamExtension(video)
audio = getBestAudioStream(youtube.streams)
audioExtension = getStreamExtension(audio)

print("Downloading video...")
video.download()
print("Downloading audio...")
audio.download(filename=audio.title+"_audio")

print("Resolving chapters")
j = json.loads(os.popen('youtube-dl -j ' + url).read())
chapters = j['chapters']
fstr = ""
for c in chapters:
	fstr = fstr + """[CHAPTER]
TIMEBASE=1/10
START="""+str(c['start_time']*10)+"""
END="""+str(c['end_time']*10)+"""
title="""+str(c['title'])+"""

"""

videoTitle = video.title.replace(' ', '\ ').replace(':', '').replace(',', '')

print("Combining audio & video and burying chapters...")

os.system('ffmpeg -i '+videoTitle+'.'+videoExtension+' -f ffmetadata '+PYTHONSCRIPTSUPPORTFILE)
with open("PYTHONSCRIPTSUPPORTFILE", "a") as myfile:
	myfile.write(fstr)
    
os.system('ffmpeg -i '+videoTitle+'.webm -i '+videoTitle+'_audio.'+audioExtension+' -i '+PYTHONSCRIPTSUPPORTFILE+' -map_metadata 1 -c:v copy -c:a aac '+videoTitle+'.mp4')

print("Finishing up")
os.remove(PYTHONSCRIPTSUPPORTFILE)
os.system('rm ' + videoTitle+'.'+videoExtension)
os.system('rm ' + videoTitle+'_audio.'+audioExtension)

print("Everything done! Please check github.com/AlexPerathoner!")





