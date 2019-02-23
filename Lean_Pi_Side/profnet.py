import time
from cProfile import run

f = open("pinet.py")
code = f.read()
f.close()

run(code, filename="profile.txt")
