from playsound import playsound
import time


CLEAR = '\033[2J'
CLEAR_AND_RETURN = '\033[H'
def Alarm(alarm_time):
    time_elapsed = 0
    print(CLEAR)
    while time_elapsed < alarm_time:
        time.sleep(1)
        time_elapsed += 1
        time_remaining = alarm_time - time_elapsed
        print(f"{CLEAR_AND_RETURN}Time remaining: {time_remaining} seconds")
        print(CLEAR_AND_RETURN)

    print("Alarm is ringing!")
    playsound('alarm.wav')
Alarm(10)  # Set alarm for 10 seconds