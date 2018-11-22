# -*- coding: utf-8 -*-
import pexpect

PROMPT = ['# ', '>>> ', '> ', '\$ ']
def send_command(child, cmd):
    child.sendline(cmd)   # 连接成功后发送命令
    child.expect(PROMPT)  # 使用expect来捕捉字符
    print child.before


def connect(user, host, password):
    ssh_newkey = 'Are you sure want to continue connecting'
    connStr = user + '@' + host
    child = pexpect.spawn('/usr/bin/ssh', [connStr])  # 第一个参数是启动命令的程序，第二个是的传入该程序的命令
    ret = child.expect([pexpect.TIMEOUT, ssh_newkey, '[P|p]assword:'])  # 捕捉字符符合就返回1
    if ret == 0:
        print '[-] Error Connecting'
        return
    if ret == 1:
        child.sendline('yes')
        ret = child.expect([pexpect.TIMEOUT, '[P|p]assword:'])
    if ret == 0:
        print '[-] Error Connecting'
        return
    child.sendline(password)
    child.expect(PROMPT)
    return child


def main():
    host = '10.10.10.130'
    user = 'vchase'
    password = 'vchase'
    child = connect(user, host, password)
    send_command(child, 'ls')


if __name__ == '__main__':
    main()