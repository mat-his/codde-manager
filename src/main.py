#!/usr/bin/env python
import getopt
import re
import sys
import argparse

# TEMP = echo $(($(</sys/class/thermal/thermal_zone0/temp) / 1000))
# TEMP = echo \$((\$(</sys/class/thermal/thermal_zone0/temp) / 1000))
# MEM = free -m | grep Mem | awk '{print (\$3/\$2)*100 \"%\"}'
# CPU = lscpu | awk '/CPU MHz/{if(\$NF+0>1000)printf \"%.3f GHz\\n\",\$NF/1000; else printf \"%.3f MHz\\n\",\$NF}'
# DISK USAGE = df -h | grep /dev/root | awk '{print \$3 \"/\" \$2}'

# ANSI REGEX (python) = # r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]'
from services import run, install


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', '-i', dest='installation', type=str, help='install some services used with Dopy app')
    parser.add_argument('--run', '-r', dest='running', type=str, help='run some services used in Dopy app')
    parser.add_argument('--vncpwd', dest='vncpwd', type=str, help='define vnc password. required for setup remote desktop')
    parser.add_argument('--mysqlpwd', dest='mysqlpwd', type=str, help='define mysql password. required for setup guacamole service')
    parser.add_argument('--guacpwd', dest='guacpwd', type=str, help='define guacamole password. required for setup guacamole service')
    parser.add_argument('--display', '-d', dest='display', type=str, help='setup default VNC display number')
    parser.add_argument('--definition', '-def', dest='definition', type=str, help='setup default screen definition for VNC sessions')
    args = parser.parse_args()

    vncpwd = args.vncpwd if args.vncpwd else "raspberry"
    mysqlpwd = args.mysqlpwd if args.mysqlpwd else "S3cur3Pa$$w0rd"
    guacpwd = args.guacpwd if args.guacpwd else "P@s$W0rD"
    display = args.display if args.display else ':1'
    definition = args.definition if args.definition else '1200x800'
    if args.display:
        pattern = re.compile(":[0-9]+")
        if not pattern.match(args.display):
            print("'display' argument must have the right syntax :<number>")
            exit(1)
    if args.installation:
        if args.installation == 'guacamole':
            print('guacamole installation')
            install.guacamole(vncpwd, mysqlpwd, guacpwd, display, definition)
            # install.test(vncpwd, mysqlpwd, guacpwd, display, definition)
    elif args.running:
        if args.running == 'websockets':
            print('starting websockets')

if __name__ == "__main__":
    main()

"""    try:
        opts, args = getopt.getopt(argv, "hi:r:b", ["install=", "run=", "bootup="])
    except getopt.GetoptError:
        print('dopy -i <service_a> -r <service_b> -b <service_b>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-mysqlpwd':
            mysqlpwd = arg
        if opt == '-vncpwd':
            vncpwd = arg
        if opt == '-h':
            print('dopy -i <service_a> -r <service_b> -b <service_b>')
            sys.exit()
        elif opt in ("-i", "--install"):
            # inputfile = arg
            print('installation service is running...')
            if arg == 'guacamole':
                install.guacamole(vncpwd, mysqlpwd)
            elif arg == 'vncserver':
                install.vncserver()

        elif opt in ("-r", "--run"):
            if arg == 'vncserver':
                run.vncserver()
            else:
                run.webserver(arg)"""
