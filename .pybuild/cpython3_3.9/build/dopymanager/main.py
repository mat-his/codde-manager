#!/usr/bin/env python
import argparse
import re
from dopymanager.exc import install, run


# ANSI REGEX (python) = # r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]


# TEMP = echo $(($(</sys/class/thermal/thermal_zone0/temp) / 1000))
# TEMP = echo \$((\$(</sys/class/thermal/thermal_zone0/temp) / 1000))
# MEM = free -m | grep Mem | awk '{print (\$3/\$2)*100 \"%\"}'
# CPU = lscpu | awk '/CPU MHz/{if(\$NF+0>1000)printf \"%.3f GHz\\n\",\$NF/1000; else printf \"%.3f MHz\\n\",\$NF}'
# DISK USAGE = df -h | grep /dev/root | awk '{print \$3 \"/\" \$2}'


def arg_checker(arg, msg):
    if not arg:
        print(msg)
        exit(1)


def main():
    # todo: PRINT LICENSE
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', '-i', dest='installation', type=str, help='install some services used with Dopy app')
    parser.add_argument('--run', '-r', dest='running', type=str, help='run some services used in Dopy app')
    parser.add_argument('--user', '-u', dest='user', type=str, help='define which user will connect to VNC. required for setup remote desktop')
    parser.add_argument('--vncpwd', dest='vncpwd', type=str, help='define vnc password. required for setup remote desktop')
    parser.add_argument('--mysqlpwd', dest='mysqlpwd', type=str, help='define mysql password. required for setup guacamole service')
    parser.add_argument('--guacpwd', dest='guacpwd', type=str, help='define guacamole password. required for setup guacamole service')
    parser.add_argument('--display', '-d', dest='display', type=str, help='setup default VNC display number')
    parser.add_argument('--definition', '-def', dest='definition', type=str, help='setup default screen definition for VNC sessions')
    parser.add_argument('--kill', '-k', dest='stop', type=str, help='setup default screen definition for VNC sessions')
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
            arg_checker(args.user, 'missing required argument [--user USER]')
            user = args.user
            print('guacamole installation')
            install.guacamole(user, vncpwd, mysqlpwd, guacpwd, display, definition)
        elif args.installation == 'test':
            arg_checker(args.user, 'missing required argument [--user USER]')
            user = args.user
            install.test(user, vncpwd, mysqlpwd, guacpwd, display, definition)
        if args.installation == 'dashboard':
            # arg_checker(args.user, 'missing required argument [--user USER]')
            install.dashboard(args.user)
        if args.installation == 'w-keyboard':
            # arg_checker(args.user, 'missing required argument [--user USER]')
            install.w_keyboard(args.user)
        if args.installation == 'vncserver':
            arg_checker(args.user, 'missing required argument [--user USER]')
            user = args.user
            install.vncserver(user, vncpwd, display, definition)
    if args.running:
        if args.running == 'dashboard':
            print('starting websockets')
            run.webserver('dashboard')
        if args.running == 'w-keyboard':
            print('w-keyboard')
            run.webserver('w-keyboard')
        else:  # all
            run.webserver('all')
    elif args.stop:
        if args.stop == 'w-keyboard' or args.stop == 'dashboard':
            run.stop(args.stop)
        elif args.stop == 'vncserver':
            run.stop_vnc()
        # else: do_something()


if __name__ == "__main__":
    main()
