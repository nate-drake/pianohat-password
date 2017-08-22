#!/usr/bin/env python

import glob
import os
import re
import signal
import time
import bcrypt
import hashlib
from sys import exit
from Crypto.Cipher import AES

try:
    import pygame
except ImportError:
    exit("This script requires the pygame module\nInstall with: sudo pip install pygame")

import pianohat

firstpw=[]

BANK = os.path.join(os.path.dirname(__file__), "sounds")

print("""
Welcome to the Piano password configuration. 

Start playing your password now. 

Press the 'Instrument' button when you're done.

Press CTRL+C to exit.
""".format(BANK))

FILETYPES = ['*.wav', '*.ogg']
samples = []
files = []
octave = 0
octaves = 0

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

patches = glob.glob(os.path.join(BANK, '*'))
patch_index = 0

if len(patches) == 0:
    exit("Couldn't find any .wav files in: {}".format(BANK))


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

def encode_text():
    print "Encoding text..."
    key = finalpw
    IV = 16 * '\x00'          
    mode = AES.MODE_CFB
    encryptor = AES.new(key, mode, IV=IV)
	
    text = raw_input("Enter the text you wish to encode:")

    #Pad the input string.

  
    while len(text) % 16 != 0:
        text += ' '
    

    #Encrypt the text

    ciphertext = encryptor.encrypt(text)

    ciphertext

    #Save encrypted text

    c= open(".pianovault","w+")
    c.write(ciphertext)
    c.close()
    print "Encoded text has been saved." 
    exit()

def load_samples(patch):
    global samples, files, octaves, octave
    files = []
    print('Loading Samples from: {}'.format(patch))
    for filetype in FILETYPES:
        files.extend(glob.glob(os.path.join(patch, filetype)))
    files.sort(key=natural_sort_key)
    octaves = len(files) / 12
    samples = [pygame.mixer.Sound(sample) for sample in files]
    octave = int(octaves / 2)


pianohat.auto_leds(True)


def handle_note(channel, pressed):
    channel = channel + (12 * octave)
    if channel < len(samples) and pressed:
        print channel
	firstpw.append(channel)
        samples[channel].play(loops=0)


def confirm_password(channel, pressed):
    if pressed:	
        print "Your password is", firstpw

	for x in range (0,len(firstpw)):
	 	samples[firstpw[x]].play(loops=0)
		time.sleep(0.7)

     	print "Generating Password hash..."
	global finalpw
	# First convert the firstpw list to a string...
	strpw = str(firstpw)
	#Next hash this string using md5 to produce a 16 byte value
	#This allows it to be used as an encryption key for AES later.
	finalpw = hashlib.md5(strpw).hexdigest()
	# Hash and salt the password itself using Bcrypt
	hashed = bcrypt.hashpw(finalpw, bcrypt.gensalt())
	# Save the password to a hidden file named .pianohash
	f= open(".pianohash","w+")
	f.write(hashed)
	f.close()
	print "Password has been saved." 
	# Launch procedure to encode text....
	encode_text()
	
	


def handle_octave_up(channel, pressed):
    global octave
    if pressed and octave < octaves:
        octave += 1
        print('Selected Octave: {}'.format(octave))


def handle_octave_down(channel, pressed):
    global octave
    if pressed and octave > 0:
        octave -= 1
        print('Selected Octave: {}'.format(octave))


pianohat.on_note(handle_note)
pianohat.on_octave_up(handle_octave_up)
pianohat.on_octave_down(handle_octave_down)
pianohat.on_instrument(confirm_password)

load_samples(patches[patch_index])

signal.pause()
