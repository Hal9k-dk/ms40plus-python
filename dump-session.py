import pickle

from ms40plus import Window


with open("session", "rb") as infile:
    session = pickle.load(infile)
for args in session:
    win = Window(int(args[0][2:5]))
    print(*args, win)
