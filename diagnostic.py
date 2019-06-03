"""
Script utilizado para comprobar el estado de un módulo, borrando automáticamente logs antiguos, poniendo la fecha
correcta en caso de que se haya desconfigurado y lanzando el jar de AUTOCITS.
"""


from datetime import datetime
from traceback import format_exc

from pexpect import pxssh
import argparse


def log(msg, state='normal'):
    msg = format(msg, '<30')
    if state == 'error':
        state = format(error(), '<10')
    elif state == 'ok':
        state = format(ok(), '<10')
    elif state == 'warn':
        state = format(warn(), '<10')
    else:
        state = format('', '<10')

    print(msg + state)


def ok():
    return ' \x1b[7;32;40m' + '  [OK]  ' + '\x1b[0m'


def error():
    return ' \x1b[5;30;41m' + ' [ERROR] ' + '\x1b[0m'


def warn():
    return ' \x1b[7;33;40m' + ' [WARN] ' + '\x1b[0m'


def check_gps(session: pxssh):
    s.sendline('')


def check_date(session: pxssh):
    print()
    log("Checking date")
    session.sendline("date +\"%F %T\"")
    session.prompt()
    console_date = session.before.decode().split('\r\n')[1]
    station_date = datetime.strptime(console_date, '%Y-%m-%d %H:%M:%S')
    delta = datetime.now() - station_date

    if delta.total_seconds() > 200:
        log("  Detected incorrect date", 'error')
        session.sendline(f"date -s \"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"")
        session.sendline("hwclock -w")
        session.prompt()
        session.before
        log("  Date fixed", 'ok')
    else:
        log("  Correct date", 'ok')


def check_autocits(session: pxssh):
    print()
    log("Checking AUTOCITS...")
    session.sendline("ps aux | grep java | wc -l")
    session.prompt()
    javas = int(session.before.decode().split('\r\n')[-2])

    if javas == 2:
        log("  JAR running normally", 'ok')
    elif javas == 1:
        log("  JAR not running", 'error')
        log("  Starting JAR...")
        session.sendline("java -jar AUTOCITS.jar&")
        session.prompt()
        check_autocits(session)
    else:
        log("  Several AUTOCITS running", 'error')
        log("  Killing & starting...")
        session.sendline("killall -9 java")
        session.prompt()
        log(f"  Killed all JARS")
        session.sendline("java -jar AUTOCITS.jar&")
        session.prompt()
        log("  JAR started", 'ok')
        check_autocits(session)


def clean_logs(session: pxssh):
    def count_logs(session, home=False):
        if home:
            session.sendline("ls /home/debian/GNF | wc -l")
        else:
            session.sendline("ls /root/GNF | wc -l")

        session.prompt()
        return int(session.before.decode().split('\r\n')[-2])

    print()
    try:
        print("Cleaning root logs...")
        if count_logs(session):
            log(f"  Found {count_logs(session)} logs", 'warn')
            session.sendline('rm -rf /root/GNF/*')
            s.prompt()
        else:
            log("  No logs found", 'ok')

    except Exception:
        print("  Error in logs root")

    try:
        log("Cleaning debian logs...")
        if count_logs(session):
            log(f"  Found {count_logs(session, home=True)} logs", 'warn')
            session.sendline('rm -rf /home/debian/GNF/*')
            s.prompt()
        else:
            log("  No logs found", 'ok')

    except Exception:
        log("  Could not perform logs clean", 'error')

    if count_logs(session) == 0:
        log("  All logs cleaned", 'ok')
    else:
        log(f"{count_logs(session)} logs could not be removed", 'error')


if __name__ == '__main__':
    RSA = '/home/jorge/PycharmProjects/V2Xdiagnostic/id_rsa'

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", type=str, default='root', help="SSH user")
    parser.add_argument("-p", "--password", type=str, default='debian', help="SSH password")
    parser.add_argument("-ip", "--host", type=str, default='192.168.0.2', help="V2X IP")
    parser.add_argument("-rsa", "--rsa", type=str, default=None, help="SSH RSA key")
    args = parser.parse_args()

    s = pxssh.pxssh()
    try:
        if not s.login(args.host, args.user, args.password, sync_multiplier=6, auto_prompt_reset=True, login_timeout=15,
                       ssh_key=args.rsa):
            log("SSH session failed on login", 'error')
            str(s)
        else:
            log("SSH session login successful", 'ok')
            # print(str(s.before).replace("\\r\\n", "\n"))
            check_autocits(s)
            clean_logs(s)
            check_date(s)
            s.logout()
    except:
        log("SSH session failed on login", 'error')
        print(format_exc())
