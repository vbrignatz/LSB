# General info

This program use the least significant bits of the Red and Green channel of a png file to hide or read a message.

# How to use 

To write a message in a picture :
```
./main.py -f images/rgb.png -t "this is a very secret message I don't want anybody to see"
```

To read a message from a picture :
```
./main.py --filename hidden.png --mode read
```

the hidden message will be saved in `hidden.txt`

## PNG types

This program works with all kind of png files (greyscale, greyscale+alpha, rgb, rgba, palette or not).
