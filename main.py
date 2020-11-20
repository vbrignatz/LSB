#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" main.py: Read or write a message in a png file using LSB method

usage: main.py [-h] -f FILENAME -o OUTPUT [-t TEXT] [-m {write,read}]
optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        The filename to use
  -t TEXT, --text TEXT  The top secret text to be sent
  -m {write,read}, --mode {write,read}
                        Read to read a msg from a png, wrtie to write a msg in a png

Author : Vincent Brignatz
"""


import png
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Read or write a message in a png file using LSB method')
parser.add_argument('-f', "--filename", type=str, required=True,
                    help='The filename to use')
parser.add_argument('-t', "--text", type=str, default=None,
                    help='The top secret text to be sent')
parser.add_argument('-m', "--mode", type=str, choices=["write", "read"], default="write",
                    help="Read to read a msg from a png, wrtie to write a msg in a png")

args = parser.parse_args()

def hide_message(rgba_img, message):
    """ Write the lsb from R and G channel of the picture to hide the message.
        (List<List<Tuple<int>>>, str) ~> (List<List<Tuple<int>>>)

        >>> hide_message([[2, 4, 6, 8, 10, 12, 14, 16], [32, 64, 65, 33, 7, 8, 9, 0]], "\x04\xff\x0a")
        [[0, 5, 4, 8, 11, 15, 15, 19], [34, 66, 64, 32, 7, 8, 9, 0]]
    """
    width = int(len(rgba_img[0]) / 4)
    for k, char in enumerate(message):
        i, j = k%width, int(k/width)
        ord_char = ord(char)
        # hide the char :
        # 2 lsb in red
        # then 2 in blue
        # 2 in green
        # and the 2 msb in alpha
        for n in range(4):
            rgba_img[j][i*4+n] = (rgba_img[j][i*4+n] & 0b11111100) + ((ord_char & (0b11 << n*2)) >> n*2)
    return rgba_img

def find_message(rgba_img):
    """ Read the lsb from R and G channel, contatenate them to find the message hidden in the picture.
        (List<List<Tuple<int>>>) ~> (str)

        >>> find_message([[6, 1, 3, 0, 6, 2, 6, 0], [6, 3, 3, 0, 7, 8, 9, 0]])
        "abcx"
    """
    msg = ""
    for row in rgba_img:
        for i in range(0, len(rgba_img[0])-3, 4):
            char = 0
            for n in range(4):
                char += (row[i+n] & 0b11) << n*2
            msg += chr(char)
    return msg

if __name__ == "__main__":
    # Read the image
    r=png.Reader(filename=args.filename)
    width, height, rows, infos = r.asRGBA8()
    rgba_img = [list(r) for r in rows]

    if args.mode == "write":
        # Check we have a message
        if args.text is None:
            parser.print_help()
            print("main.py: error: the following arguments are required when in writing mode: -t/--text")
            exit(0)

        args.text = args.text.encode("ascii", "ignore").decode()

        print(f"Hiding '{args.text}' in hidden.png from image {args.filename}")

        # sanity check
        n_px = width * height
        n_msg = len(args.text)
        if n_px < n_msg:
            raise MemoryError(f"The text ({n_msg} chars) is too fat for the image you have choosen ({n_px} pixels)")

        # hide the message
        new_rgba_img = hide_message(rgba_img, args.text)

        # save new image in hidden.png 
        w = png.Writer(width, 30, bitdepth=8, greyscale=False, alpha=True)
        f = open("hidden.png", 'wb')
        w.write(f, new_rgba_img[:30])

    elif args.mode == "read":
        # Find the message
        msg = find_message(rgba_img)
        output = subprocess.check_output(["strings"], input=bytes(msg, "utf-8"))
        print(output.split(b'\n')[0])