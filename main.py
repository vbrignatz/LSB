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

def merge_number(h_part, l_part):
    """ Merge two 4 bits parts into a byte
        (int, int) ~> (int)

        >>> merge_number(0b1010, 0b0101)
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

def create_palette(rgb_img):
    """ Create a list of all unique element from rgb_img
        (List<List<Tuple<int>>>) ~> (List<Tuple<int>>)

        >>> create_palette([[(1, 2, 3), (4, 5, 6)], [(1, 2, 3), (7, 8, 9)]])
        [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
    """
    palette = []
    for row in rgb_img:
        for px in row:
            if px not in palette:
                palette.append(px)
    return palette

def int_to_rgb_img(int_img, palette):
    """ Put the element of palette in int_img by using the indice in int_img.
        This is usefull to convert the palette system of pypng to a rgb matrix.
        (List<List<int>>) ~> (List<List<Tuple<int>>>)

        >>> int_to_rgb_img([[0, 1], [0, 2]], [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
        [[(1, 2, 3), (4, 5, 6)], [(1, 2, 3), (7, 8, 9)]]
    """
    rgb_img = []
    for r in int_img:
        rgb_img.append([])
        for px in r:
            rgb_img[-1].append(palette[px])
    return rgb_img

def rgb_to_int_img(rgb_img, palette):
    """ Replace the rgb tuples of rgb_img by their indices in the palette.
        This is usefull to convert a rgb matrix to the palette system of pypng.
        (List<List<Tuple<int>>>) ~> (List<List<int>>)

        >>> rgb_to_int_img([[(1, 2, 3), (4, 5, 6)], [(1, 2, 3), (7, 8, 9)]],
                            [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
        [[0, 1], [0, 2]]
    """
    int_img = []
    for row in rgb_img:
        int_img.append([])
        for px in row:
            int_img[-1].append(palette.index(px))
    return int_img

def hide_message(rgb_img, message):
    """ Write the lsb from R and G channel of the picture to hide the message.
        (List<List<Tuple<int>>>, str) ~> (List<List<Tuple<int>>>)

        >>> hide_message([[(1, 2, 3, 0), (4, 5, 6, 0)], [(1, 2, 3, 0), (7, 8, 9, 0)]], "abc")
        [[(6, 1, 3, 0), (6, 2, 6, 0)], [(6, 3, 3, 0), (7, 8, 9, 0)]]
    """
    new_rgb_img = []
    i = 0
    for row in rgb_img:
        new_rgb_img.append([])
        for px in row:
            if i < len(message):
                h, l = split_number(ord(message[i]))
                new_px = (
                            replace_lsb(px[0], h),
                            replace_lsb(px[1], l),
                            px[2],
                            px[3]
                        )
                new_rgb_img[-1].append(new_px)
            else:
                new_rgb_img[-1].append(px)
            i+=1
    return new_rgb_img

def find_message(rgb_img):
    """ Read the lsb from R and G channel, contatenate them to find the message hidden in the picture.
        (List<List<Tuple<int>>>) ~> (str)

        >>> hide_message([[(6, 1, 3, 0), (6, 2, 6, 0)], [(6, 3, 3, 0), (7, 8, 9, 0)]])
        "abcx"
    """
    msg = ""
    for row in rgb_img:
        for px in row:
            _, h = split_number(px[0])
            _, l = split_number(px[1])
            msg += chr(merge_number(h, l))
    return msg

if __name__ == "__main__":
    # Read the image
    r=png.Reader(filename=args.filename)
    width, height, rows, infos = r.read()

    int_img = [list(r) for r in rows]
    rgb_img = int_to_rgb_img(int_img, infos["palette"])


    if args.mode == "write":
        # Check we have a message
        if args.text is None:
            parser.print_help()
            print("main.py: error: the following arguments are required when in writing mode: -t/--text")
            exit(0)

        print(f"Hiding '{args.text}' in {args.output} from image {args.filename}")

        # sanity check
        n_px = len(rgb_img[0]) * len(rgb_img)
        n_msg = len(args.text)
        if n_px < n_msg:
            raise MemoryError(f"The text ({n_msg} chars) is too fat for the image you have choosen ({n_px} pixels)")

        # hide the message
        new_rgb_img = hide_message(rgb_img, args.text)

        # save new image in out.png
        palette = create_palette(new_rgb_img)
        new_int_img = rgb_to_int_img(new_rgb_img, palette)
        w = png.Writer(len(new_int_img[0]), len(new_int_img), palette=palette, bitdepth=8)
        f = open(args.output, 'wb')
        w.write(f, new_int_img)

    elif args.mode == "read":
        # Find the message
        msg = find_message(rgb_img)

        # Write the message in the ouput file
        with open(args.output, "w") as fout:
            fout.write(msg)