# How to use 

To write a message in a picture :
```
./main.py -f mr-muscle.png -o hidden.png -t "this is a very secret message I don't want anybody to see" -m write
```

To read a message from a picture :
```
./main.py -f hidden.png -o hidden.txt -m read
```

the hidden message will be saved in `hidden.txt`