import json
import time
import websockets
import os
import asyncio
import socket
import re
from pynput.keyboard import Key, Controller


def escape_ansi(txt):
    ansi_escape = re.compile(r'((\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]|\x1b\(B)')  # \x1b\(B is a custom regex
    return ansi_escape.sub('', txt)


def tab_to_space(txt):
    txt_space = re.compile(r'[ ]+')
    return txt_space.sub(' ', txt)


def dashboard():
    output = {
        'data': {}
    }
    # temp
    output["data"]["temp"] = os.popen("vcgencmd measure_temp | tr -dc '[0-9].\n\r'").read().strip()
    # echo $(($(</sys/class/thermal/thermal_zone0/temp) / 1000))
    # mem
    output["data"]["mem"] = os.popen("""free -m | grep Mem | awk '{ print ($3/$2)*100 }'""").read().strip()
    # cpu
    # output["data"]["cpu"] = os.popen("lscpu | awk '/CPU MHz/{if($NF+0>1000)printf \"%.3f GHz\\n\",$NF/1000; else "
    #                                  "printf \"%.3f MHz\\n\",$NF}'").read()
    output["data"]["cpu"] = \
        os.popen(
            """vcgencmd measure_clock arm | awk ' BEGIN { FS="=" } ; { print $2 / 1000000000 } '""").read().strip()
    output["data"]["max_cpu"] = \
        os.popen(
            """lscpu | grep -i 'CPU max MHZ' | tr -dc '[0-9],\n\r' | awk '{ print $1 / 1000 }'""").read().strip()
    # disk
    output["data"]["disk"] = os.popen(
        "df -h | grep /dev/root | awk '{ print $3 \"/\" $2 }' | tr -d 'G'").read().strip()
    # voltage
    output["data"]["voltage"] = os.popen("vcgencmd measure_volts core | tr -dc '[0-9].\n\r'").read().strip()
    # "sudo dmidecode --type processor | grep Voltage | awk '{print $2 $3}'"
    # tasks
    output["data"]["tasks"] = tab_to_space(escape_ansi(os.popen("top -n 1 | sed -n -e 8,18p").read()).strip())
    # print(output)
    return json.dumps(output)


def nothing():
    return 'no data'


async def dashboard_handler(websocket, path, service):
    # data = await websocket.recv()
    # reply = f"Data received as: {data} !"
    # await websocket.send(reply)
    print('handler')
    # while True:
    async for msg in websocket:
        await websocket.send(dashboard())
        print('send !')
    # time.sleep(10)


async def keyboard_handler(websocket, path):
    async for key in websocket:
        keyboard = Controller()
        keyboard.press(key)
        keyboard.release(key)
        await websocket.send('wrote : ', key)
        print('send !')


def webserver(service):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    print('get sock name : ' + s.getsockname()[0])
    # hostname = socket.gethostbyname(socket.gethostname())
    sockname = s.getsockname()[0]

    if service == 'dashboard':
        start_server = websockets.serve(dashboard_handler, sockname, 7450)
        asyncio.get_event_loop().run_until_complete(start_server)
    elif service == 'w-keyboard':
        start_server = websockets.serve(keyboard_handler, sockname, 8160)
        asyncio.get_event_loop().run_until_complete(start_server)
    else:  # all
        start_server1 = websockets.serve(dashboard_handler, sockname, 7450)
        start_server2 = websockets.serve(keyboard_handler, sockname, 8160)
        asyncio.get_event_loop().run_until_complete(start_server1)
        asyncio.get_event_loop().run_until_complete(start_server2)

    asyncio.get_event_loop().run_forever()



def vncserver():
    return os.popen("x11vnc -display :0 -clip 1920x1080+1600+0 -autoport -localhost rfbauth /home/pi/.vnc_passwd -nopw -bg -o /var/log/x11vnc.log -xkb -ncache 0 -ncache_cr -quiet -forever").read().strip()
# todo: remplacer par systemctl start x11vnc@2.service
