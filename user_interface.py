from time import sleep
import threading

i = 0

def say_hi(i):
    while True:
        print(str(i) + 'hi')
        sleep(1)

def go():
    while True:
        global i
        if not i%2:
            t = threading.Thread(target=say_hi, args=(i,))
            t.start()
        i += 1
        sleep(1)

def p():
    while True:
        t = threading.Thread(target=go, args=())
        t.start()
        print('ok')
        sleep(1)

p()
