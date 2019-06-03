"""
Script utilizado para instalar la iso base en un módulo
"""

import argparse
import subprocess
from pathlib import Path

tmp: Path = Path('/tmp/clone')
TITLE = '*' * 10


def umount(unit: str) -> None:
    """
    Function to unmount a unit.

    :param unit: Unit to unmount.
    :type unit: str
    """

    try:
        print(f'{TITLE}  Desmontando unidad {unit}  {TITLE}')
        subprocess.run(['umount', f'{unit}'])
    except Exception:
        print(f"No se pudo desmontar la unidad {unit}")
        exit(-1)
    else:
        print(f'{TITLE}  Unidad desmontada  {TITLE}')


def clone(image: str, unit: str) -> None:
    """
    Function to clone a image to the CF card

    :param image: The .iso image
    :param unit: The target unit
    """

    cmd_list = ['dd', f'if={image}', f'of={unit}', 'bs=1M', 'status=progress']
    try:
        print(f'{TITLE}  Clonando imagen {args.image}  {TITLE}')
        dd = subprocess.Popen(cmd_list)
        dd.wait()

    except Exception:
        print(f"No se pudo clonar la imagen {args.image}")
        exit(-1)
    else:
        print(f'{TITLE}  Imagen clonada  {TITLE}')


def format_unit(unit: str, name: str = '') -> None:
    """
    Function to format a CF CARD

    :param unit: The target unit
    :param name: Label name
    """
    format_list = ['mkfs.ext4', '-F', '-m 0', f'-L V2X-{name}', f'{unit}']

    try:
        print(f'{TITLE}  Formateando unidad {unit}  {TITLE}')
        subprocess.run(format_list)
    except Exception:
        print(f"No se pudo desmontar la unidad {unit}")
    else:
        print(f'{TITLE}  Unidad desmontada  {TITLE}')


def mount(unit: str) -> None:
    """
    Function to mount a CF card

    :param unit: Target
    """
    global tmp

    try:
        print(f'{TITLE}  Montando unidad {args.card}  {TITLE}')
        if not tmp.exists():
            subprocess.run(['mkdir', '/tmp/clone'])
        subprocess.run(['mount', f'{unit}1', '/tmp/clone'])
    except Exception:
        print(f"No se pudo montar la unidad {unit}")
    else:
        print(f'{TITLE}  Unidad Montada en {tmp}  {TITLE}')


def edit_files() -> None:
    """
    Function to edit the files needed to the new station
    """

    HOSTNAME = tmp.joinpath('etc', 'hostname')
    HOSTAPD = tmp.joinpath('etc', 'hostapd', 'hostapd.conf')
    HOSTS = tmp.joinpath('etc', 'hosts')
    RULES = tmp.joinpath('etc', 'udev', 'rules.d')
    HISTORY = tmp.joinpath('root', '.bash_history')
    INTERFACES = tmp.joinpath('etc', 'network', 'interfaces')

    # Hostname must be equal to the host local loopback
    print(f"Escribiendo {HOSTNAME}")
    with open(str(HOSTNAME), 'w') as file:
        file.write(f'V2X-{args.id}')

    print(f"Escribiendo {HOSTS}")
    with open(str(HOSTS), 'w') as file:
        file.write('127.0.0.1	localhost\n')
        file.write(f'127.0.1.1	V2X-{args.id}\n')
        file.write('::1     localhost ip6-localhost ip6-loopback\n')
        file.write('ff02::1 ip6-allnodes\n')
        file.write('ff02::2 ip6-allrouters\n')

    print(f"Escribiendo {INTERFACES}")
    with open(str(INTERFACES), 'w') as file:
        file.write('auto lo\n')
        file.write('iface lo inet loopback\n\n')
        file.write('auto eth0\n')
        file.write('#allow-hotplug eth0\n')
        file.write('#iface eth0 inet dhcp\n')
        file.write('iface eth0 inet static\n')

        if args.id == 1:
            idx = 254
        else:
            idx = args.id

        file.write(f'address 192.168.0.{idx}\n')
        file.write('netmask 255.255.255.0\n\n')

        file.write('auto wlan0\n')
        file.write('iface wlan0 inet static\n')
        file.write('hostapd /etc/hostapd/hostapd.conf\n')
        file.write('address 192.168.1.1\n')
        file.write('netmask 255.255.255.0\n')

    # 2.4 GHZ WIFI configuration
    print(f"Escribiendo {HOSTAPD}")
    with open(str(HOSTAPD), 'w') as file:
        file.write('interface=wlan0\n')
        file.write('driver=nl80211\n')
        file.write(f'ssid=V2X-{args.id}\n')
        file.write('channel=1\n')
        file.write('wpa=3\n')
        file.write('wpa_key_mgmt=WPA-PSK\n')
        file.write('wpa_passphrase=V2X_stati0n\n')
        file.write('rsn_pairwise=CCMP\n')
    
    print(f"Borrando  {RULES}")    
    subprocess.run(['rm', '-rf', str(RULES)])
    subprocess.run(['mkdir', str(RULES)])
    print(f"Borrando historial de comandos")
    subprocess.run(['rm', str(HISTORY)])
    subprocess.run(['touch', str(HISTORY)])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", type=Path, help="Image to clone", required=True)
    parser.add_argument("-o", "--card", type=Path, help="Target card", required=True)
    parser.add_argument("-id", "--id", type=int, help="Module ID", required=True)

    args = parser.parse_args()
    args.image: Path
    args.card: Path

    if not args.image.exists():
        print(f"El archivo {args.image} no existe")
        exit(-1)

    if not args.image.is_file():
        print(f"{args.image} no es un archivo")
        exit(-1)

    if not args.card.exists():
        print(f"El directorio {args.card} no existe")
        exit(-1)

    if args.card.is_file():
        print(f"{args.image} es un archivo")
        exit(-1)

    umount(str(args.card) + '1')
    format_unit(str(args.card))
    clone(str(args.image), str(args.card))
    mount(str(args.card))
    edit_files()
    umount(str(tmp))

    print("Clonación finalizada")
