import os
import subprocess
import sys

from services.term_colors import TermColors as Colors

guacamole_properties = """# Hostname and port of guacamole proxy
guacd-hostname: localhost
guacd-port:     4822

# Auth provider class (authenticates user/pass combination, needed if using the provided login screen)
auth-provider: net.sourceforge.guacamole.net.basic.BasicFileAuthenticationProvider
basic-user-mapping: /etc/guacamole/user-mapping.xml"""

# on some distribution, service unit path isn't lib but usr


def package_check(args):
    devnull = open(os.devnull, "w")
    retval = subprocess.call(args, stdout=devnull, stderr=subprocess.STDOUT)
    devnull.close()
    return retval == 0


def user_mapping_file(user, encrypted_passwd, default_passwd):
    return f"""<user-mapping>

    <!-- Per-user authentication and config information -->
    <authorize
         username="{user}"
         password="{encrypted_passwd}"
         encoding="md5">
      
       <connection name="dopy_session">
         <protocol>vnc</protocol>
         <param name="hostname">localhost</param>
         <param name="port">5901</param>
         <param name="password">{default_passwd}</param>
         <param name="enable-audio">true</param>
       </connection>
    </authorize>

</user-mapping>"""


def vnc_service_file(user, definition):  # todo: user !!!
    # username = user  # os.popen("whoami").read().strip()
    return f"""[Unit]
Description=a wrapper to launch an X server for VNC
After=syslog.target network.target

[Service]
Type=simple

ExecStartPre=-/usr/bin/vncserver -kill :%i > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry {definition} -localhost :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target"""


def guacamole(user, vncpwd="raspberry", mysqlpwd="S3cur3Pa$$w0rd", guacpwd="P@s$W0rD", display=':1',
              definition='1200x800'):
    print('guacamole installation and connection setup')

    if not package_check(['which', 'guacd']):
        print("Package guacd not installed. Proceed to installation. ")
        print('\n== SYSTEM UPDATE ! ==\n')
        os.system("sudo apt update")

        if not (package_check(['dpkg', '-s', 'git'])):
            print('\n== INSTALLING GIT ==\n')
            os.system('sudo apt install git -y')
        if not package_check(['dpkg', '-s', 'git']):
            print(Colors.FAIL + 'E: Unable to install git' + Colors.RESET)
            exit(2)
        print('\n== CLONE GIT SCRIPT ==\n')
        os.system('git clone https://github.com/MysticRyuujin/guac-install.git /tmp/guac-install')
        os.system('chmod +x /tmp/guac-install/./guac-install.sh')
        os.system(
            f"/tmp/guac-install/./guac-install.sh --nomfa --installmysql --mysqlpwd {mysqlpwd} --guacpwd {guacpwd}")
        print('\n== CHECKING STATUS ==\n')
        os.system('systemctl status tomcat9 guacd mysql --no-pager --full')
        os.system('sudo ss -antup | grep "mysqld\|guacd\|java"')
    else:
        print("guacd already installed\n")

    print('\n== GUACAMOLE CONFIGURATION ==\n')
    out_f = open("/etc/guacamole/guacamole.properties", "w")
    out_f.writelines(guacamole_properties)
    out_f.close()
    encrypted_passwd_output = os.popen(
        f"echo -n {vncpwd} | openssl md5").read().strip()
    encrypted_passwd_output = encrypted_passwd_output.split()[1]
    # si guacamole directory existe, sinon problème
    out_mapping = open("/etc/guacamole/user-mapping.xml", "w")
    out_mapping.writelines(user_mapping_file(user, encrypted_passwd_output, vncpwd))
    out_mapping.close()

    print('\n== DESKTOP ENVIRONMENT ==\n')
    if (package_check(['ls', '/usr/bin/*-session']) or (
            package_check(['dpkg', '-s', 'raspberrypi-ui-mods']) and package_check(
        ['dpkg', '-s', 'xinit']) and package_check(['dpkg', '-s', 'xserver-xorg']))):
        print('desktop environment already installed')
    else:
        print(Colors.FAIL + 'ERROR: no desktop environment installed (xfce or pixel)')

    if not "tigervnc" in os.popen('dpkg -l | grep vnc').read().strip():  # todo: the right way ?
        print(Colors.RESET + '\n no vncserver installed. Installing TigerVNC... \n')
        os.system("sudo apt install tigervnc-standalone-server -y")
    if not package_check(['which', 'vncserver']) or not "tigervnc" in os.popen(
            'dpkg -l | grep vnc').read().strip():  # todo: the right way ?
        print(Colors.FAIL + 'E: Unable to install TigerVNC (tigervnc-standakibe-server)' + Colors.RESET)
        exit(2)
    print('setup password')
    if not os.path.exists(f"/home/{user}/.vnc"):
        os.mkdir(f"/home/{user}/.vnc")
    os.system(f"echo {vncpwd} | vncpasswd -f > /home/{user}/.vnc/passwd")
    os.system(f"chown -R {user}:{user} /home/{user}/.vnc")
    os.system(f"chmod 0600 /home/{user}/.vnc/passwd")
    print('vnc password created')
    print('\n== VNC SERVER AS SERVICE ==\n')
    out_vnc = open("/lib/systemd/system/dopy-manager-vncserver@.service", "w")
    out_vnc.writelines(vnc_service_file(user, definition))
    out_vnc.close()
    os.system(f"vncserver -kill {display}")
    os.system("systemctl daemon-reload")
    os.system(f"sudo systemctl start dopy-manager-vncserver@{display}.service")
    os.system(f"sudo systemctl enable dopy-manager-vncserver@{display}.service")
    os.system(f"sudo systemctl status dopy-manager-vncserver@{display}.service --no-pager --full")
    os.system("sudo ss -lnpt | grep vnc")


def vncserver():
    print('vncserver installation')


def reverse_proxy():
    print('setup reverse proxy if user want it')


def test(user, vncpasswd="raspberry", mysqlpasswd="S3cur3Pa$$w0rd", guacpasswd="P@s$W0rD", display=':1',
         definition='1200x800'):
    print('user => ', user)
    print('vncpwd => ', vncpasswd)
    print('mysqlpwd => ', mysqlpasswd)
    print('guacpwd => ', guacpasswd)
    print('display => ', display)
    print('definition => ', definition)


def create_service(service_name, path, desc, start, stop, user='', pre='', post=''):
    out_vnc = open(f"dopy-manager-{path}{service_name}.service", "w")
    line_pre = f"ExecStartPre={pre}" if pre else ''
    line_post = f"ExecStartPost={post}" if post else ''
    line_user = f"User={user}" if user else ''
    # todo: LICENSE
    # WorkingDirectory=/usr/share/dopy-manager/
    lines = f"""[Unit]
Description={desc}
After=syslog.target network.target

[Service]
{line_user}
Type=notify
ConditionPathExists=/usr/bin/dopy-manager

{line_pre}
ExecStart={start}
{line_post}
ExecStop={stop}
ExecReload={stop + '&&' + start}
Restart=on-failure

[Install]
WantedBy=multi-user.target"""

    out_vnc.writelines(lines)
    out_vnc.close()
    os.system("systemctl daemon-reload")
    os.system(f"sudo systemctl start dopy-manager-{service_name}.service")
    os.system(f"sudo systemctl enable dopy-manager-{service_name}.service")
    os.system(f"sudo systemctl status dopy-manager-{service_name}.service --no-pager --full")


def dashboard(username):
    print('dashboard as a service')
    """create_service(
        "dashboard",
        "/lib/systemd/system/",
        "Send realtime dashboard data about computer state to Dopy app",
        start="/usr/bin/dopy-manager -r dashboard",
        stop="/usr/bin/dopy-manager -k dashboard"
    )"""


def w_keyboard(username):
    print('w-keyboard as a service')
    """create_service(
        "w-keyboard",
        "/lib/systemd/system/",
        "Send keyboard keys inputs from Dopy app to this computer",
        start="/usr/bin/dopy-manager -r w-keyboard",
        stop="/usr/bin/dopy-manager -k w-keyboard",
        user="root",
    )"""
