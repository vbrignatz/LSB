import png
import argparse

parser = argparse.ArgumentParser(description='Hide a message in a png file using LSB method')
parser.add_argument('-f', "--filename", type=str, required=True,
                    help='The filename to use')
parser.add_argument('-m', "--message", type=str,  required=True,
                    help='The top secret message to be sent')

args = parser.parse_args()

def split_number(n):
    """ split a byte in two 4 bits parts """
    if n > 0b11111111:
        raise AttributeError("The number given is not a Byte")
    h_part = (n & 0b11110000) >> 4
    l_part =  n & 0b1111
    return h_part, l_part

def merge_number(h_part, l_part):
    if h_part > 0b1111 or l_part > 0b1111:
        raise AttributeError("The parts given is not a 4 bits digits")
    return (h_part << 4) + l_part

def replace_bits(number, bits):
    return (number & 0b11110000) + bits

def create_palette(rgb_img):
    palette = []
    for row in rgb_img:
        for px in row:
            if px not in palette:
                palette.append(px)
    return palette

def int_to_rgb_img(int_img, palette):
    rgb_img = []
    for r in int_img:
        rgb_img.append([])
        for px in r:
            rgb_img[-1].append(infos["palette"][px])
    return rgb_img

def rgb_to_int_img(rgb_img, palette):
    int_img = []
    for row in rgb_img:
        int_img.append([])
        for px in row:
            int_img[-1].append(palette.index(px))
    return int_img

def hide_message(rgb_img, message):
    new_rgb_img = []
    i = 0
    for row in rgb_img:
        new_rgb_img.append([])
        for px in row:
            if i < len(message):
                h, l = split_number(ord(message[i]))
                new_px = (
                            replace_bits(px[0], h),
                            replace_bits(px[1], l),
                            px[2],
                            px[3]
                        )
                new_rgb_img[-1].append(new_px)
            else:
                new_rgb_img[-1].append(px)
            i+=1
    return new_rgb_img

if __name__ == "__main__":
    print(f"Hiding '{args.message}' in out.png from image {args.filename}")

    r=png.Reader(filename=args.filename)
    width, height, rows, infos = r.read()

    int_img = [list(r) for r in rows]
    rgb_img = int_to_rgb_img(int_img, infos["palette"])

    #TODO : Check if im size if enought for msg len

    new_rgb_img = hide_message(rgb_img, args.message)

    # save new image in out.png
    palette = create_palette(new_rgb_img)
    new_int_img = rgb_to_int_img(new_rgb_img, palette)
    w = png.Writer(len(new_int_img[0]), len(new_int_img), palette=palette, bitdepth=8)
    f = open('out.png', 'wb')
    w.write(f, new_int_img)
