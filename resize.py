#!/usr/bin/env python3
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"    Telegram Sticker Resizer                                 "
"    Resize images to fit telegram sticker size limitations.  "
"    Author : @jaidTw                                         "
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import cv2
import os
import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image

MAX_HEIGHT = 512
MAX_WIDTH = 512
WAIFU2X = False
OUTPUT_DIR = './out/'
FORCE_OVERWRITE = False
EXT_SUPPORT = ['.png', '.jpg', '.bmp', '.jpeg']
WAIFU2X_BIN = "waifu2x-ncnn-vulkan-20210521-windows\waifu2x-ncnn-vulkan.exe"
WAIFU2X_OUTPUT_DIR = "./_waifu2x_tmp/"

def banner():
    print('[-] --- Telegram Sticker Resizer ---')
    print('    Resize images to fit the telegram sticker size restrictions.')

def help():
    print('    Usage: ./resize.py [-f] [-h] [-w] <input_path>')
    print('        -f : Force overwriting.')
    print('        -h : Show this helping message.')
    print('        -w : Use Waifu2x to scale the image first')
    print('        input_path : Path for input images.')


def resize(fname):
    img = cv2.imread(fname.as_posix(), cv2.IMREAD_UNCHANGED)
    if img is None:
        print("[ERROR] Can't load %s, probably broken? Skipping" % fname)
        return 0, 0, 1

    height, width, _ = img.shape
    print("        Size : %d x %d" % (height, width))
    if (height == 512 and width <= MAX_WIDTH) or \
       (height <= MAX_HEIGHT and width == 512):
        print("        Size already feasible. Skipping")
        return 0, 1, 0

    scale = min(MAX_HEIGHT / height, MAX_WIDTH / width)
    new = cv2.resize(img, None, fx=scale, fy=scale,
                     interpolation=cv2.INTER_AREA)
    print("        Resized : %d x %d, scale = %f" % (*new.shape[:2], scale))

    fname = fname.stem + '.png'
    output = OUTPUT_DIR / fname
    if output.is_file():
        if not FORCE_OVERWRITE:
            print("\n%s already exists, overwrite? (y/N)" % output,
                  file=sys.stderr)
            opt = input()
            if opt == '' or opt[0].lower() != 'y':
                print('    File exists. Skipping')
                return 0, 1, 0
    elif output.is_dir():
        print('[ERROR] %s is an existing directory. Skipping' % output)
        return 0, 0, 1
    if not cv2.imwrite(output.as_posix(), new):
        print("[ERROR] Failed to save output to %s. Skipping" % output)
        return 0, 0, 1
    print("        Successfully saved to %s" % output)
    return 1, 0, 0


def main():
    global OUTPUT_DIR, FORCE_OVERWRITE, WAIFU2X

    banner()
    if '-h' in sys.argv:
        help()
        exit()
    if '-f' in sys.argv:
        FORCE_OVERWRITE = True
        sys.argv.remove('-f')
    if '-w' in sys.argv:
        WAIFU2X = True
        sys.argv.remove('-w')
    if len(sys.argv) > 1:
        INPUT_DIR = Path(sys.argv[1])

    if not INPUT_DIR.exists():
        print("[ERROR] \"%s\" doest not exist" % INPUT_DIR)
        exit()
    if not INPUT_DIR.is_dir():
        print("[ERROR] \"%s\" is not a directory" % INPUT_DIR)
        exit()
    
    OUTPUT_DIR = INPUT_DIR / 'out'
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
    except PermissionError:
        print('[ERROR] Failed to create %s, permission denied.' %
              OUTPUT_DIR)
        exit()
    if not os.access(OUTPUT_DIR, os.W_OK):
        print('[ERROR] No permission to write in %s.' %
              OUTPUT_DIR)
        exit()

    cnt = (0, 0, 0)
    try:
        if WAIFU2X:
            print('[-] Fixing alpha channel in case of it\'s wrong.')
            # fix alpha channel in original image in case it's ill-formed
            for fname in INPUT_DIR.iterdir():
                if fname.suffix in EXT_SUPPORT:
                    img = Image.open(fname.as_posix())
                    if img.mode == "L" or img.mode == "P":
                        img.convert("RGBA").save(fname.as_posix())  

            print('[-] Using Waifu2x to scale the image')
            waifu2x_output = INPUT_DIR / WAIFU2X_OUTPUT_DIR
            try:
                waifu2x_output.mkdir(exist_ok=True)
            except PermissionError:
                print('[ERROR] Failed to create %s, permission denied.' %
                    waifu2x_output)
                exit()
            if not os.access(waifu2x_output, os.W_OK):
                print('[ERROR] No permission to write in %s.' %
                    waifu2x_output)
                exit()
            subprocess.run([WAIFU2X_BIN, "-i", INPUT_DIR.absolute(), "-o", waifu2x_output.absolute(), "-x", "-n",  "2"])
            
            for fname in INPUT_DIR.iterdir():
                if fname.suffix in EXT_SUPPORT:
                    print("[-] Opening %s ..." % fname)
                    cnt = tuple(map(sum, zip(cnt, resize(fname))))
            
            shutil.rmtree(waifu2x_output)
        else:
            for fname in INPUT_DIR.iterdir():
                if fname.suffix in EXT_SUPPORT:
                    print("[-] Opening %s ..." % fname)
                    cnt = tuple(map(sum, zip(cnt, resize(fname))))
        print('[-] Done.')
    except KeyboardInterrupt:
        print('[-] Interrupted.')
    print('[-] %d file(s) processed, %d file(s) skipped, %d error(s) occured.'
          % cnt)


if __name__ == '__main__':
    main()

