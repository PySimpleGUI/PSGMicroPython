from machine import Pin
import select
import time
import sys
import _thread


#          888~-_                  e88~-_                 888
# 888  888 888   \  Y88b  /       d888   \  e88~-_   e88~\888  e88~~8e
# 888  888 888    |  Y888/        8888     d888   i d888  888 d888  88b
# 888  888 888   /    Y8/         8888     8888   | 8888  888 8888__888
# 888  888 888_-~      Y          Y888   / Y888   ' Y888  888 Y888    ,
# "88_-888 888        /            "88_-~   "88_-~   "88_/888  "88___/
#                  _/


# Communication back to the GUI is done using a simple print
print('STARTING uPython code...')

# Anti-pattern anywone?  Cheating to get global variables so that the code isn't peppered with global statements

class G:
    stop_requested = False
    blink_led = False
    input_pin:Pin = None
    pin_map = {}        # dictionary of pin to pin num

# 888~-_                               ,e,
# 888   \   e88~~8e   e88~~\  e88~~8e   "  Y88b    /  e88~~8e
# 888    | d888  88b d888    d888  88b 888  Y88b  /  d888  88b
# 888   /  8888__888 8888    8888__888 888   Y88b/   8888__888
# 888_-~   Y888    , Y888    Y888    , 888    Y8/    Y888    ,
# 888 ~-_   "88___/   "88__/  "88___/  888     Y      "88___/
#
# ~~~888~~~ 888                                888
#    888    888-~88e  e88~~8e    /~~~8e   e88~\888
#    888    888  888 d888  88b       88b d888  888
#    888    888  888 8888__888  e88~-888 8888  888
#    888    888  888 Y888    , C888  888 Y888  888
#    888    888  888  "88___/   "88_-888  "88_/888


def receive_thread():
    print('Serial Receive Thread STARTED')
    while True:
        # See if chars are available on the serial port
        r, _, _ = select.select([sys.stdin], [], [], 2.0)
        if r:
            line = sys.stdin.readline().strip()
            if not line:
                continue
            if line.startswith('TEST'):
                for i in range(10):
                    print(f'Test {i}')
                    time.sleep(.2)
            elif line.startswith('STOP'):
                print('uPython serial thread EXITING....')
                G.stop_requested = True
                _thread.exit()
            elif line.startswith('LED'):
                print('Starting LED blink test')
                G.blink_led = True
            else:
                print(f'Received unknown command: {line}')



# 888            d8                                                d8
# 888 888-~88e _d88__  e88~~8e  888-~\ 888-~\ 888  888 888-~88e  _d88__ 
# 888 888  888  888   d888  88b 888    888    888  888 888  888b  888   
# 888 888  888  888   8888__888 888    888    888  888 888  8888  888   
# 888 888  888  888   Y888    , 888    888    888  888 888  888P  888   
# 888 888  888  "88_/  "88___/  888    888    "88_-888 888-_88"   "88_/ 
#                                                      888


@micropython.native
def chip_interrupt(pin:Pin):
    try:
        pin_num = G.pin_map[pin]
    except:
        print('Error pin lookup')
        pin_num = None
    print(f'Interrupt on pin {pin_num}')


def blink_led():
    led = Pin(25, Pin.OUT)  # use any free GPIO pin number

    for i in range(0,20):
        led.value(1)				# optimized call
        time.sleep(.5)
        led.value(0)
        time.sleep(.5)
        if G.stop_requested:
            return


#      e    e                ,e,
#     d8b  d8b       /~~~8e   "  888-~88e
#    d888bdY88b          88b 888 888  888
#   / Y88Y Y888b    e88~-888 888 888  888
#  /   YY   Y888b  C888  888 888 888  888
# /          Y888b  "88_-888 888 888  888

def main():
    print('Started MAIN')
    G.input_pin = Pin(2, Pin.IN)
    G.pin_map[G.input_pin] = 2
    G.input_pin.irq(chip_interrupt, Pin.IRQ_FALLING)

    _thread.start_new_thread(receive_thread, ())

    print('DONE starting uPython code')
    # background / work loop
    while True:
        time.sleep(3)
        if G.stop_requested:
            print('uPython code EXITING')
            break
        elif G.blink_led:
            blink_led()
            G.blink_led = False
            print('LED Blink Test Complete')
    sys.exit()

if __name__ == '__main__':
    main()

