import time


def timer(target_time):
    start_time = time.time()
    while True:
        current_time = time.time()
        diff = current_time - start_time
        print(diff)

        if diff >= target_time:
            print('Time up!')
            break
        time.sleep(1)