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
Welcome to the Piano Decoder. 

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

def decode_text():
    print "Decoding text..."
    key = finalpw
    IV = 16 * '\x00'          
    mode = AES.MODE_CFB
    decryptor = AES.new(key, mode, IV=IV)

# Open the saved ciphertext file:
        
    d= open(".pianovault","r") 
    # Read the encrypted text 
    vaulttext = d.readline()
    d.close()
    

    #Decrypt the text

    plain = decryptor.decrypt(vaulttext)

    #Display decrypted text

    print plain

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

	global finalpw
	# Convert the password to 16 byte string so we can use it for encryption key
	# This doesn't offer any extra security. 
	# First convert the firstpw list to a string...
	strpw = str(firstpw)
	finalpw = hashlib.md5(strpw).hexdigest()

	# Open the saved password hash file as read only:
        f= open(".pianohash","r")
	# Read the bcrypt password has from the file
	bhash = f.readline()
	f.close()
	# If password is correct then launch procedure to decode text:
	if bcrypt.checkpw(finalpw, bhash):
    		print "Password is correct."
		decode_text()
	else:
    		print "Password incorrect."
		exit()
	


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
