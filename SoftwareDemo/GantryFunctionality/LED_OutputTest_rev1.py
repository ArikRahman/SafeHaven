from gpiozero import LED
from time import sleep

led1 = LED(17)
led2 = LED(27)
led3 = LED(22)
led4 = LED(23)

print("LED Test Starting...")

while True:
    led1.on()
    sleep(1)
    led2.on()
    sleep(1)
    led3.on()
    sleep(1)
    led4.on()
    sleep(1)
    led1.off()
    led2.off()
    led3.off()
    led4.off()
    sleep(1)
