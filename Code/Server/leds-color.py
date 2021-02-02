from Led import Led
import sys

print('Setting LEDs color')
print('Args=' + ' '.join(sys.argv))
led = Led()

if len(sys.argv) >= 4:
    led.allColor(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
else:
    led.allColor(2, 2, 15)
print("Bye")