import os
import subprocess

from coddemanager.utils.term_colors import TermColors as Colors

guacamole_properties = """# Hostname and port of guacamole proxy
guacd-hostname: localhost
guacd-port: 4822

# Auth provider class (authenticates user/pass combination, needed if using the provided login screen)
auth-provider: net.sourceforge.guacamole.net.basic.BasicFileAuthenticationProvider
basic-user-mapping: /etc/guacamole/user-mapping.xml"""


# on some distribution, service unit path isn't lib but usr


def package_check(args) -> bool:
    """Check if package exist in the system.

    Args:
        args: Package in question.

    Returns: True if package is already installed.

    """
    devnull = open(os.devnull, "w")
    retval = subprocess.call(args, stdout=devnull, stderr=subprocess.STDOUT)
    devnull.close()
    return retval == 0


def user_mapping_file(user: str, encrypted_passwd: str, default_passwd: str) -> str:
    """
    User Mapping file template.

    Returns: Completed User mapping file with custom credentials.

    Args:
        user (str): Name of user authorized to use vnc session.
        encrypted_passwd (str): New encrypted password.
        default_passwd (str): New default passwd."""

    return f"""<user-mapping>

    <!-- Per-user authentication and config information -->
    <authorize
         username="{user}"
         password="{encrypted_passwd}"
         encoding="md5">
      
       <connection name="codde_session">
         <protocol>vnc</protocol>
         <param name="hostname">localhost</param>
         <param name="port">5901</param>
         <param name="password">{default_passwd}</param>
         <param name="enable-audio">true</param>
       </connection>
    </authorize>

</user-mapping>"""


def vnc_service_file(definition: str) -> str:
    # username = user  # os.popen("whoami").read().strip()
    """System Service file template.

    Args:
        definition: Specify the VNC display definition.

    Returns:
        Completed VNC system service file with custom parameters.
    """

    return f"""[Unit]
Description=a wrapper to launch an X server for VNC
After=syslog.target network.target

[Service]
Type=forking

ExecStartPre=-/usr/bin/vncserver -kill :%i > /dev/null 2>&1
ExecStart=/usr/bin/vncserver -depth 24 -geometry {definition} -localhost :%i
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target"""


def guacamole(user: str, vncpwd="raspberry", mysqlpwd="S3cur3Pa$$w0rd", guacpwd="P@s$W0rD", display=':1',
              definition='1200x800'):
    """Steps to install Guacamole service automatically and perform user customizations.

    Args:
        user: User which use guacamole configuration.
        vncpwd: Password for VNC session.
        mysqlpwd: Password for MySQL server.
        guacpwd: Password required by the Guacamole's installation.
        display: Display identifier (e.g :1).
        definition: Definition of the display.

    Returns:
        None.
    """

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

    vncserver(user, vncpwd, display, definition)


def vncserver(user: str, vncpwd: str, display: str, definition: str):
    """Install requirements to create vncserver and setup service to start it at boot up.

    Args:
        user: User which use VNC server on his configuration path /home/{user}/.
        vncpwd: Required password to configure VNC. Password stored in /home/{user}/.vnc/passwd.
        display: Display identifier (e.g :1).
        definition: Definition of the display.

    Returns: None.

    """
    print('\n== VNCSERVER SERVICE INSTALLATION ==\n')
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
    out_vnc = open("/lib/systemd/system/coddemanager-vncserver@.service", "w")
    out_vnc.writelines(vnc_service_file(user, definition))
    out_vnc.close()
    os.system(f"vncserver -kill {display}")
    os.system("systemctl daemon-reload")
    os.system(f"sudo systemctl start coddemanager-vncserver@{display}.service")
    os.system(f"sudo systemctl enable coddemanager-vncserver@{display}.service")
    os.system(f"sudo systemctl status coddemanager-vncserver@{display}.service --no-pager --full")
    os.system("sudo ss -lnpt | grep vnc")


def reverse_proxy():
    """Reverse proxy configuration.
    Todo:
        * setup reverse proxy if user want"""
    print('setup reverse proxy if user want it')


def test(user, vncpasswd="raspberry", mysqlpasswd="S3cur3Pa$$w0rd", guacpasswd="P@s$W0rD", display=':1',
         definition='1200x800'):
    """Guacamole parameters test.

    Args:
        user: Name of user allowed to install and run guacamole.
        vncpwd: Password for VNC session.
        mysqlpwd: Password for MySQL server.
        guacpwd: Password required by the Guacamole's installation.
        display: Display identifier (e.g :1).
        definition: Definition of the display.

    Todo:
        * use it inside unit tests
        * return all values as map (and exit code 0 ?)

    Returns: None

    """
    print('user => ', user)
    print('vncpwd => ', vncpasswd)
    print('mysqlpwd => ', mysqlpasswd)
    print('guacpwd => ', guacpasswd)
    print('display => ', display)
    print('definition => ', definition)


def create_service(service_name: str, path: str, desc: str, start: str, stop='', user='', pre='', post=''):
    """System service creation template.

    Args:
        service_name: Name of new created service.
        path: Path of executable.
        desc: Description of the service.
        start: When script starts.
        stop: When script is stopped.
        user: Deprecated.
        pre: Script executed before initialization of this service.
        post: Script executed after initialization of this service.

    Returns: None.

    """
    out_vnc = open(f"{path}coddemanager-{service_name}.service", "w")
    line_pre = f"ExecStartPre={pre}" if pre else ''
    line_post = f"ExecStartPost={post}" if post else ''
    line_user = f"User={user}" if user else ''
    line_stop = f"ExecStop={stop}" if stop else ''
    # todo: LICENSE
    # WorkingDirectory=/usr/share/coddemanager/
    lines = f"""[Unit]
Description={desc}
After=syslog.target network.target

[Service]
{line_user}
Type=simple

{line_pre}
ExecStart={start}
{line_post}
{line_stop}
Restart=on-failure
RestartSec=10
KillMode=process

[Install]
WantedBy=multi-user.target"""

    out_vnc.writelines(lines)
    out_vnc.close()
    os.system("systemctl daemon-reload")
    os.system(f"sudo systemctl start coddemanager-{service_name}.service")
    os.system(f"sudo systemctl enable coddemanager-{service_name}.service")
    os.system(f"sudo systemctl status coddemanager-{service_name}.service --no-pager --full")


def dashboard():
    """Install dashboard as service to start at boot up.

    Returns: None.

    """

    print('dashboard as a service')
    create_service(
        "dashboard",
        "/lib/systemd/system/",
        "CODDE Manager - dashboard",
        start="/usr/bin/coddemanager -r dashboard"
    )


def w_keyboard():
    """Install wireless keyboard as service to start at boot up.

        Returns: None.

        """

    print('w-keyboard as a service')
    create_service(
        "w-keyboard",
        "/lib/systemd/system/",
        "CODDE manager - wireless keyboard",
        start="/usr/bin/coddemanager -r w-keyboard"
    )
    # crontask("python /home/pi/coddemanager/main.py -r w-keyboard")
