import json
import time
import websockets
import os
import asyncio
import socket
import re
# from pynput.keyboard import Key, Controller
import keyboard
import daemon
import subprocess
import sys
import traceback


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
    output["data"]["temp"] = subprocess.run("vcgencmd measure_temp | tr -dc '[0-9].\n\r'", shell=True,
                                            capture_output=True, text=True).stdout
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
    # output["data"]["tasks"] = tab_to_space(escape_ansi(subprocess.run("top -n -b 1 | sed -n -e 8,18p", shell=True, capture_output=True, text=True).stdout))
    output["data"]["tasks"] = tab_to_space(
        subprocess.run("ps -o pid,user,time,%cpu,%mem,command ax | sort -b -k3 -r | sed -n -e 2,22p", shell=True,
                       capture_output=True, text=True).stdout)
    # todo: benchmark top vs ps command
    # print(output)
    # print(output["data"]["tasks"])
    return json.dumps(output)


def nothing():
    return 'no data'


async def dashboard_handler(websocket):
    # data = await websocket.recv()
    # reply = f"Data received as: {data} !"
    # await websocket.send(reply)
    # print('handler')
    # while True:
    async for msg in websocket:
        await websocket.send(dashboard())
        # print('send !')
    # time.sleep(10)


async def keyboard_handler(websocket):
    # keyboard = Controller()
    # print('keyboard handler')
    async for key in websocket:
        try:
            txt = str(key)
            if len(txt) > 1:  # shortcut / sentence output
                if 'dopy_esc#' in txt:
                    esc = re.compile(r'dopy_esc#')
                    content = esc.sub('', txt)
                    keyboard.send(content)
                    await websocket.send('[' + content + ']')
                else:
                    if '\u001B' in key:
                        keyboard.write(key)
                    else:
                        keyboard.write(txt)
                    # callback
                    await websocket.send(txt)
            else:  # classic output
                keyboard.send(txt)
                # print('key pressed !')
                # callback
                if txt == '\r' or txt == '\n':
                    await websocket.send('\r\n')
                else:
                    await websocket.send(txt)
                    # print('send' + txt)
        except Exception:
            print('E: ' + str(sys.exc_info()[2]))
            print(traceback.format_exc())
            await websocket.send(str(sys.exc_info()[2]))


def webserver(service):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    # print('get sock name : ' + s.getsockname()[0])
    # hostname = socket.gethostbyname(socket.gethostname())
    sockname = s.getsockname()[0]

    async def serve(choice):
        if choice == 'dashboard':
            # print('dashboard')
            # todo: si 7450 n'est pas déja utilisé. sinon print "impossible de démarrer le service"
            async with websockets.serve(dashboard_handler, sockname, 7450):
                print('listening')
                await asyncio.Future()
        elif choice == 'w-keyboard':
            # print('choice == w-keyboard')
            # todo: si 8160 n'est pas déja utilisé. sinon print "impossible de démarrer le service"
            async with websockets.serve(keyboard_handler, sockname, 8160):
                print('listening')
                await asyncio.Future()
        else:  # all
            # todo: si 7450 et 8160 n'est pas déja utilisé. sinon print "impossible de démarrer le service"
            async with websockets.serve(dashboard_handler, sockname, 7450):
                await asyncio.Future()
            async with websockets.serve(keyboard_handler, sockname, 8160):
                await asyncio.Future()

    # with daemon.DaemonContext():
    asyncio.run(serve(service))


def stop(service):
    # asyncio.get_event_loop().call_soon_threadsafe(asyncio.get_event_loop().stop)
    print('E: do not stop process with this method')


def stop_vnc():
    print('not yet implemented')


def vncserver():
    return os.popen(
        "x11vnc -display :0 -clip 1920x1080+1600+0 -autoport -localhost rfbauth /home/pi/.vnc_passwd -nopw -bg -o /var/log/x11vnc.log -xkb -ncache 0 -ncache_cr -quiet -forever").read().strip()
# todo: remplacer par systemctl start x11vnc@2.service
