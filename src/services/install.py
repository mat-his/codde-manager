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


def package_check(args):
    devnull = open(os.devnull, "w")
    retval = subprocess.call(args, stdout=devnull, stderr=subprocess.STDOUT)
    devnull.close()
    return retval == 0


def user_mapping_file(encrypted_passwd, default_passwd):
    return f"""<user-mapping>

    <!-- Per-user authentication and config information -->
    <authorize
         username="{os.popen("whoami").read().strip()}"
         password="{encrypted_passwd}"
         encoding="md5">
      
       <connection name="default">
         <protocol>vnc</protocol>
         <param name="hostname">localhost</param>
         <param name="port">5901</param>
         <param name="password">{default_passwd}</param>
       </connection>
    </authorize>

</user-mapping>"""


def vnc_service_file(definition):
    username = os.popen("whoami").read().strip()
    return f"""[Unit]
Description=a wrapper to launch an X server for VNC
After=syslog.target network.target

[Service]
Type=forking
User={username}
Group={username}
WorkingDirectory=/home/{username}

ExecStartPre=-/usr/bin/vncserver -kill :%i > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry {definition} -localhost :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target"""


def guacamole(vncpwd="raspberry", mysqlpwd="S3cur3Pa$$w0rd", guacpwd="P@s$W0rD", display=':1',
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
        os.system('systemctl status tomcat9 guacd mysql')
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
    # todo: si guacamole directory existe, sinon problème
    out_mapping = open("/etc/guacamole/user-mapping.xml", "w")
    out_mapping.writelines(user_mapping_file(encrypted_passwd_output, vncpwd))
    out_mapping.close()

    print('\n== DESKTOP ENVIRONMENT ==\n')
    if (package_check(['ls', '/usr/bin/*-session']) or (
            package_check(['dpkg', '-s', 'raspberrypi-ui-mods']) and package_check(
        ['dpkg', '-s', 'xinit']) and package_check(['dpkg', '-s', 'xserver-xorg']))):
        print('desktop environment already installed')
    else:
        print(Colors.FAIL + 'ERROR: no desktop environment installed (xfce or pixel)')

    if not package_check(['which', 'vncserver']):
        print(Colors.RESET + '\n no vncserver installed. Installing TigerVNC... \n')
        os.system("sudo apt install tigervnc-standalone-server -y")
    if not package_check(['which', 'vncserver']):
        print(Colors.FAIL + 'E: Unable to install TigerVNC (tigervnc-standakibe-server)' + Colors.RESET)
        exit(2)
    out_vnc = open("/etc/systemd/system/vncserver@.service", "w")
    out_vnc.writelines(vnc_service_file(definition))
    out_vnc.close()
    os.system(f"vncserver -kill {display}")
    os.system(f"sudo systemctl start vncserver@{display}.service")
    os.system(f"sudo systemctl enable vncserver@{display}.service")
    os.system(f"sudo systemctl status vncserver@{display}.service")
    os.system("sudo ss -lnpt | grep vnc")


def vncserver():
    print('vncserver installation')


def reverse_proxy():
    print('setup reverse proxy if user want it')


def test(vncpasswd="raspberry", mysqlpasswd="S3cur3Pa$$w0rd", guacpasswd="P@s$W0rD", display=':1',
         definition='1200x800'):
    print('vncpwd => ', vncpasswd)
    print('mysqlpwd => ', mysqlpasswd)
    print('guacpwd => ', guacpasswd)
    print('display => ', display)
    print('definition => ', definition)
