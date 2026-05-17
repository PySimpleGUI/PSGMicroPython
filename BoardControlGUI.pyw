import PySimpleGUI as sg
import serial
import serial.tools.list_ports
import time
import pathlib
import os

"""
    BoardControlGUI
    
    PySimpleGUI program to interface with a MicroPython based microcontroller.
    Features
        * Upload Micropython code to microcontrollers sucb a Raspberryt Pi or ESP32 boards
        * Send commands to your micropython program
        * Display messages/information from your micropython program
    Name your uPython file so that your filename begins with "upython_" so that
        it can be listed in the drop-down of available programs to load.
"""

#       CONSTANTS
# location of micropython files
PROGRAM_FOLDER =    r'.'

#  Prehaps an Anti-pattern       GLOBAL VARIABLES
class G:        # global variables
    ser: serial.Serial = None
    comport = None          # the comport in use




# 888     888        888                     888   888              8888888b. d8b
# 888     888        888                     888   888              888   Y88bY8P
# 888     888        888                     888   888              888    888
# 888     88888888b. 888 .d88b.  8888b.  .d88888   888888 .d88b.    888   d88P888
# 888     888888 "88b888d88""88b    "88bd88" 888   888   d88""88b   8888888P" 888
# 888     888888  888888888  888.d888888888  888   888   888  888   888       888
# Y88b. .d88P888 d88P888Y88..88P888  888Y88b 888   Y88b. Y88..88P   888       888
#  "Y88888P" 88888P" 888 "Y88P" "Y888888 "Y88888    "Y888 "Y88P"    888       888
#            888
#            888
#            888

def wait_and_read(ser, delay=0.2):
    time.sleep(delay)
    data = ser.read_all()

def enter_clean_repl(ser):
    ser.write(b"\x03")  # Ctrl-C
    ser.write(b"\x03")  # twice just in case
    ser.write(b"\x04")  # Ctrl-D soft reboot
    wait_and_read(ser, 0.5)


def send_file(ser, local_path: str):
    p = pathlib.Path(local_path)
    with p.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    #enter paste mode
    ser.write(b"\x05")  # Ctrl-E

    wait_and_read(ser, 0.1)

    for line in lines:
        line += '\n'
        ser.write(line.encode("utf-8"))
        time.sleep(0.01)

    wait_and_read(ser, 0.5)

    sg.cprint('Upload complete', text_color='red')

    # finish block and execute
    ser.write(b"\x04")  # Ctrl-D


def upload_upython_file(filename):
    sg.cprint(f'Uploading <{filename}>', text_color='red')

    enter_clean_repl(G.ser)
    send_file(G.ser, filename)


def setup_com_port() -> serial.Serial:
    comports = serial.tools.list_ports.comports()
    for port in comports:
        # print(f'{port.device} {port.product} {port.description}')
        # desc = port.description.lower() if port.description is not None else ''
        # prod = port.product.lower() if port.product is not None else ''
        if True:
            try:
                G.ser = serial.Serial(f"{port.device}", 115200, timeout=1)
                G.comport = port.device
            except Exception as e:
                print(f'{port.device} failed: {e}')
            else:
                return G.ser
    return None



def send_line(line:str):
    # Communicate with the upython program once loaded
    if len(line) != 1:      # If not a single char, add on a CRLF
        line += '\r\n'
    G.ser.write(bytes(line, encoding='-utf-8'))



#  e88~-_  888
# d888   \ 888-~88e  e88~-_   e88~-_   d88~\  e88~~8e
# 8888     888  888 d888   i d888   i C888   d888  88b
# 8888     888  888 8888   | 8888   |  Y88b  8888__888
# Y888   / 888  888 Y888   ' Y888   '   888D Y888    ,
#  "88_-~  888  888  "88_-~   "88_-~  \_88P   "88___/
#
# 888~~  ,e, 888                  e88~~\  888   | 888
# 888___  "  888  e88~~8e        d888     888   | 888
# 888    888 888 d888  88b       8888 __  888   | 888
# 888    888 888 8888__888       8888   | 888   | 888
# 888    888 888 Y888    ,       Y888   | Y88   | 888
# 888    888 888  "88___/         "88__/   "8__/  888

def choose_upload_file(use_last:bool=False):
    python_files = [file for file in os.listdir(PROGRAM_FOLDER) if file.startswith('upython_') and file.endswith('.py')]
    if use_last:
        return sg.user_settings_get_entry('-PYFILE-')

    layout = [[sg.T('Choose a file to upload')],
              [sg.Combo(python_files, k='-PYFILE-', bind_return_key=True, readonly=True, setting='Choose a file')],
              [sg.Push(), sg.OK(), sg.Cancel()]]

    window = sg.Window('Choose upload file', layout, )
    event, values = window.read(close=True)

    if event in ('OK', '-PYFILE-'):
        upload_file = values['-PYFILE-']
        window.settings_save(values)
    else:
        upload_file = None

    return upload_file

#  .d8888b.                d8b        888
# d88P  Y88b               Y8P        888
# Y88b.                               888
#  "Y888b.   .d88b. 888d888888 8888b. 888
#     "Y88b.d8P  Y8b888P"  888    "88b888
#       "88888888888888    888.d888888888
# Y88b  d88PY8b.    888    888888  888888
#  "Y8888P"  "Y8888 888    888"Y888888888
#
#
#
# 8888888b.                      888   88888888888888                                 888
# 888   Y88b                     888       888    888                                 888
# 888    888                     888       888    888                                 888
# 888   d88P .d88b.  8888b.  .d88888       888    88888b. 888d888 .d88b.  8888b.  .d88888
# 8888888P" d8P  Y8b    "88bd88" 888       888    888 "88b888P"  d8P  Y8b    "88bd88" 888
# 888 T88b  88888888.d888888888  888       888    888  888888    88888888.d888888888  888
# 888  T88b Y8b.    888  888Y88b 888       888    888  888888    Y8b.    888  888Y88b 888
# 888   T88b "Y8888 "Y888888 "Y88888       888    888  888888     "Y8888 "Y888888 "Y88888

def read_serial_thread(window:sg.Window):
    # sg.cprint('serial thread started')
    sg.cprint('Ready to upload to board')
    while True:
        try:
            line = G.ser.readline().rstrip()
        except Exception as e:
            sg.cprint('ERROR FROM SERIAL PORT... EXITING', text_color='Red')
            window.write_event_value('Error', e)        # If get a serial port error, fake Exit
            return

        if line:
            window.write_event_value('-THREAD-', line.decode('utf-8'))

#                      d8b
#                      Y8P
#
# 88888b.d88b.  8888b. 88888888b.
# 888 "888 "88b    "88b888888 "88b
# 888  888  888.d888888888888  888
# 888  888  888888  888888888  888
# 888  888  888"Y888888888888  888



def main():
    G.ser = setup_com_port()
    if G.ser is None:
        sg.popup_auto_close("cannot connect to a com port", auto_close_duration=1)
        exit()
    time.sleep(2)


    layout = [[sg.Text(f'{G.ser.port}'), sg.B('Upload to Board', k='-UPLOAD-'), sg.B('Reupload Last', k='-REUPLOAD-'), sg.T(sg.user_settings_get_entry('-PYFILE-'), k='-LAST FILEMAME-'),
                        sg.Push(), sg.T(f'COM {G.comport}')],
                [sg.Multiline(s=(80, 30), k='-ML-', write_only=True, auto_refresh=True, autoscroll=True, wrap_lines=True, reroute_cprint=True, font='courier 14', expand_x=True, expand_y=True)],
              [sg.In(s=(80,1), k='-IN-', focus=True, do_not_clear=True), sg.Button('Send',bind_return_key=True )],
               [sg.B('LED'), sg.Push(),sg.T('', k='-PAUSED-'), sg.B('Pause'), sg.B('Clear'),sg.B('Stop uPython'),sg.B('Control C'), sg.B('Exit')]]

    window = sg.Window('Data Monitor', layout, finalize=True, font='courier 14', right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT, resizable=True)

    window.start_thread(lambda : read_serial_thread(window))

    paused = False

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):        # stop upython prog when exiting
            send_line( 'STOP')
            exit()
        elif event == 'Error':
            sg.popup('Fatal error encountered', values['Error'], auto_close=True, auto_close_duration=2)
            exit()
        command = values['-IN-']
        if event == '-THREAD-':       # line of text received from serial port (over USB)
            line:str = values['-THREAD-']
            sg.cprint(line)
        elif event == 'Send':
            try:
                send_line(values['-IN-'])
            except:
                sg.cprint('ERROR trying to send command', text_color='red')
            window['-IN-'].update('')
        elif event == 'Control C':
            send_line(chr(3))
        elif event == 'Clear':
            window['-ML-'].update('')
        elif event in ('-UPLOAD-', '-REUPLOAD-'):
            filename = choose_upload_file(event == '-REUPLOAD-')
            if filename:
                upload_upython_file(os.path.join(PROGRAM_FOLDER, filename))
            else:
                sg.cprint('Upload cancelled')
        elif event == 'Stop uPython':
            send_line( 'STOP')
        elif event == 'Pause':
            paused = not paused
            if paused:
                window['-PAUSED-'].update('PAUSED')
            else:
                window['-PAUSED-'].update('')
        elif event == 'LED':
            send_line('LED')
        elif event ==  'Version':
            sg.popup(sg.get_versions(), line_width=70)

if __name__ == "__main__":
    main()