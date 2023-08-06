import re
import os
import sys
import time
import urllib
import requests
import Tkinter as tk
from PIL import Image
from bs4 import BeautifulSoup

def main():

    url = 'http://explosm.net/comics/latest'

    # get local screen dimensions
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # create canvas for where the comic will be located
    background = Image.new('RGBA', (screen_width+100,screen_height+100), (255,255,255,255))
    background_width, background_height = background.size

    while True:

        # get comic info
        link = urllib.urlopen(url)
        soup = BeautifulSoup(link, "html.parser")
        img = soup.findAll('img', {'id': "main-comic"})[0].get('src')
        img = "http://" + img[2:]
        imageName = img.split('/')[4]

        # probably a better way but oh well
        f = open('temp.png','wb')
        f.write( requests.get(img ).content )
        f.close()

        comic = Image.open('temp.png','r')
        comic_width, comic_height = comic.size

        # will have to redo this aglorithm, this one is too basic
        offset = ( (background_width - comic_width)/2, (background_height - comic_height)/2)
        offset_width, offset_height = offset

        trueSize = True
        if comic_width > background_width*1.05 or comic_height > background_height*1.05:
            trueSize = False

        trueSizeCounter = 2
        while not trueSize:
            background = Image.new('RGBA', (screen_width*trueSizeCounter,screen_height*trueSizeCounter), (255,255,255,255))
            background_width, background_height = background.size
            offset = ((background_width - comic_width)/2, (background_height - comic_height)/2)
            if comic_width > background_width*1.05 or comic_height > background_height*1.05:
                trueSize = False
                trueSizeCounter = trueSizeCounter + 1
            else:
                trueSize = True

        background.paste(comic, offset)
        background.save(imageName + '.png')

        # remove files that arent needed and set background
        os.remove("temp.png")
        osxcmd = 'osascript -e \'tell application "System Events" to set picture of every desktop to "' + "~/" + imageName + '.png' + '" \''
        os.system(osxcmd)
        os.remove(imageName + '.png')

        time.sleep(21600) # check every 6 hours for new

if __name__ == "__main__":
    main()
