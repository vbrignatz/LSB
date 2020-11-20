#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" main.py: Read or write a message in a png file using LSB method

usage: main.py [-h] -f FILENAME -o OUTPUT [-t TEXT] [-m {write,read}]
optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        The filename to use
  -o OUTPUT, --output OUTPUT
                        The output filename
  -t TEXT, --text TEXT  The top secret text to be sent
  -m {write,read}, --mode {write,read}
                        Read to read a msg from a png, wrtie to write a msg in a png

Author : Vincent Brignatz
"""


import png
import argparse

parser = argparse.ArgumentParser(description='Read or write a message in a png file using LSB method')
parser.add_argument('-f', "--filename", type=str, required=True,
                    help='The filename to use')
parser.add_argument('-o', "--output", type=str, required=True,
                    help='The output filename')
parser.add_argument('-t', "--text", type=str, default=None,
                    help='The top secret text to be sent')
parser.add_argument('-m', "--mode", type=str, choices=["write", "read"], default="write",
                    help="Read to read a msg from a png, wrtie to write a msg in a png")

args = parser.parse_args()

def split_number(n):
    """ Split a byte into two 4 bits parts 
        (int) ~> (int, int)

        >>> split_number(0b10100101)
        (0b1010, 0b0101)
    """
    if n > 0b11111111:
        raise AttributeError("The number given is not a Byte")
    h_part = (n & 0b11110000) >> 4
    l_part =  n & 0b1111
    return h_part, l_part

def concat_number(h_part, l_part):
    """ Concatenate two 4 bits numbers into a byte.
        (int, int) ~> (int)

        >>> concat_number(0b1010, 0b0101)
        0b10100101
    """
    if h_part > 0b1111 or l_part > 0b1111:
        raise AttributeError("The parts given is not a 4 bits digits")
    return (h_part << 4) + l_part

def replace_lsb(number, bits):
    """ Replace the 4 LSB by 4 bits
        (int, int) ~> (int)

        >>> replace_lsb(0b10100101, 0b1100)
        0b10101100
    """
    return (number & 0b11110000) + bits

def palette_to_rgba(idx_img, palette):
    """ Put the element of palette in idx_img by using the indice in idx_img.
        This is usefull to convert the palette system of pypng to a rgb matrix.
        (List<List<int>>) ~> (List<List<Tuple<int>>>)

        >>> palette_to_rgba([[0, 1], [0, 2]], [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
        [[1, 2, 3,  4, 5, 6], [1, 2, 3,  7, 8, 9]]
    """
    rgba_img = []
    for r in idx_img:
        rgba_img.append([])
        for px in r:
            rgba_img[-1].extend(palette[px])
    return rgba_img

def hide_message(rgba_img, message):
    """ Write the lsb from R and G channel of the picture to hide the message.
        (List<List<Tuple<int>>>, str) ~> (List<List<Tuple<int>>>)

        >>> hide_message([[1, 2, 3, 0, 4, 5, 6, 0], [1, 2, 3, 0, 7, 8, 9, 0]], "abc")
        [[6, 1, 3, 0, 6, 2, 6, 0], [6, 3, 3, 0, 7, 8, 9, 0]]
    """
    width = int(len(rgba_img[0]) / 4)
    for k, char in enumerate(message):
        h, l = split_number(ord(char))
        j = int(k/width)
        i = k%width
        rgba_img[j][i*4] = h
        rgba_img[j][i*4+1] = l
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
            _, h = split_number(row[i])
            _, l = split_number(row[i+1])
            msg += chr(concat_number(h, l))
    return msg

if __name__ == "__main__":
    # Read the image
    r=png.Reader(filename=args.filename)
    width, height, rows, infos = r.asRGBA8()
    rgba_img = [list(r) for r in rows]
    
    # convert is palette mode
    if "palette" in infos:
        rgba_img = palette_to_rgba(rgba_img, infos["palette"])

    if args.mode == "write":
        # Check we have a message
        if args.text is None:
            parser.print_help()
            print("main.py: error: the following arguments are required when in writing mode: -t/--text")
            exit(0)

        print(f"Hiding '{args.text}' in {args.output} from image {args.filename}")

        # sanity check
        n_px = width * height
        n_msg = len(args.text)
        if n_px < n_msg:
            raise MemoryError(f"The text ({n_msg} chars) is too fat for the image you have choosen ({n_px} pixels)")

        # hide the message
        new_rgba_img = hide_message(rgba_img, args.text)

        # save new image in out.png 
        w = png.Writer(width, height, bitdepth=8, greyscale=False, alpha=True)
        f = open(args.output, 'wb')
        w.write(f, new_rgba_img)

    elif args.mode == "read":
        # Find the message
        msg = find_message(rgba_img)

        # Write the message in the ouput file
        with open(args.output, "w") as fout:
            fout.write(msg)