# -*- coding:utf-8 -*-
import argparse
import socket
import threading
import sys
from datetime import datetime


# 设置线程锁
lock = threading.Lock()
# 定义线程队列
threads = []
def connscan(tgthost, tgtport, num):
    # 设置连接超时时间
    socket.setdefaulttimeout(0.5)
    type = ''
    connSkt = object
    # mode：模式0为使用默认TCP扫描，1位使用UDP扫描
    if num == '0':
        connSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        type = 'tcp'
    elif num == '1':
        connSkt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        type = 'udp'
    try:
        connSkt.connect((tgthost, tgtport))
        # 增加Banner信息(即部分信息头)
        connSkt.send('ViolentPython\r\n')
        results = connSkt.recv(103)
        # 调用线程锁，避免输出信息失序
        lock.acquire()
        print 'Scanning port: ' + str(tgtport)
        print '[+] port:{0}/{1} open'.format(tgtport, type)

        if num == '0':
            print '[+] ' + str(results)
            print '-' * 50
            connSkt.close()
    except:
        lock.acquire()
        print '[-] port:{0}/{1} closed'.format(tgtport, type)
    finally:
        lock.release()


def portscan(tgthosts, tgtports, mode):
    for tgthost in tgthosts:
        try:
            # 解析传入的主机名，检查是否有对应的IP
            tgtIP = socket.gethostbyname(tgthost)
        except:
            print "[-] Cannot resolve '%s': Unknown host" % tgthost
            return
        try:
            # 通过IP利用gethostbyaddr()方法返回一个三元组获得主机名
            tgtName = socket.gethostbyaddr(tgtIP)
            print '\n[*] Scan Results for: ' + tgtName[0]
        except:
            print '\n[*] Scan Results for: ' + tgtIP
        print '-' * 60
        t1 = datetime.now()
        for tgtport in tgtports:
            # 设置多线程扫描端口
            t = threading.Thread(target=connscan, args=(tgthost, int(tgtport), mode))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        t2 = datetime.now()
        total = t2 - t1
        print 'Scanning Completed in: ', total
        print '*' * 80 + '\n'


# 处理port_range模式传入的信息，获得新列表之后再进行扫描
def range_port(tgthost, args, mode):
    new_list_port = []
    for i in range(int(args.x[0].strip(',')), args.y[0] + 1):
        new_list_port.append(i)
    portscan(tgthost, new_list_port, mode)


# 处理port模式传入的信息
def deal_tgtport(args):
    tgtport_list = []
    for tgtport in args.port:
        # 处理传入参数时的“，”，为了两种端口传入方式都可以处理
        if ',' in tgtport:
            tgtport_list.append(tgtport.strip(','))
        else:
            tgtport_list.append(str(tgtport))
    return tgtport_list


# 处理单主机和多主机范围扫描
def deal_tgthost(args):
    # 这里使用不同的方法来处理—H传入的单参数（str类型）
    tgthost_list = args.tgthost.split(',')
    new_tgthost_list = []
    # 使用多主机扫描时，对主机列表的处理，生成新的列表
    if len(tgthost_list) == 2:
        # 同C类IP检测
        for count in range(0, 3):
            if int(tgthost_list[0].split('.')[count]) != int(tgthost_list[1].split('.')[count]):
                print 'What the IP you input is invalid'
                exit(0)

        # 获取最后一段IP的数值
        start_ip = int(tgthost_list[0].split('.')[3])
        end_ip = int(tgthost_list[1].split('.')[3])
        # 检测IP有效性
        if (start_ip > 254 or end_ip > 255) or start_ip > end_ip:
            print 'What the IP you input is invalid'
            exit(0)
        # 利用列表的rfind()方向，设置0，变为从左往右查找，输出最后一个“.”的位置
        i = tgthost_list[0].rfind('.', 0)
        for num in range(start_ip, end_ip + 1):
            # 拼成新的IP
            new_tgthost = tgthost_list[0][:i + 1] + str(num)
            new_tgthost_list.append(new_tgthost)

        return new_tgthost_list
    # 单主机时，返回的主机列表
    else:
        return tgthost_list


def deal_argument():
    parser = argparse.ArgumentParser(usage='%(prog)s This is the Scanner',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=("""Use the TCP Scanner:
    ---------------------------------------------------------------------------------------------------
    |1. Single Hostname or IP|
    -----------------------
    %(prog)s -H <target host(or ip)> [log][scan_mode][port_mode];
    -------------------------------------------------------------------
    |2. Multi IP |
    --------------
    (In this way,you can't input the hostname),You just make a small change:
    %(prog)s -H <target Ip> [log][scan_mode][port_mode];
        eg:(%(prog)s -H x.x.x.x,x.x.x.x [log][scan_mode][port_mode])
    -------------------------------------------------------------------------
            [port_mode]:
            1. port  -> eg:(%(prog)s -H x.x.x.x [log][scan_mode] port: 21, 23, 25)
            2. port_range  -> eg:(%(prog)s -H x.x.x.x [log][scan_mode] port_range: 1, 100)
            3. port_known  -> eg:(%(prog)s -H x.x.x.x [log][scan_mode] port_known)
            And you can input "%(prog)s port --help" to see the detail of each mode
            -----------------------------------------------------------------
            [scan_mode]:
            1. default  -> TCP eg:(%(prog)s -H x.x.x.x [log][port_mode])
            2. -U  -> UDP eg:(%(prog)s -H x.x.x.x -U [log][port_mode])
            -----------------------------------------------------------------
            [log]:
            1. default  -> Not log!  -> eg:(%(prog)s -H x.x.x.x [scan_mode][port_mode])
            2. -log  -> eg:(%(prog)s -H x.x.x.x -log [scan_mode][port_mode])
    --------------------------------------------------------------------------
    By the way, please pay attention to the difference between the Host(ip) and the ports when you use.
    ----------------------------------------------------------------------------------------------------"""))
    # 传入的参数是一个string，之后进行处理，单参数
    parser.add_argument('-H', dest='tgthost', type=str, help='specify target host', metavar='Hostname or Ip')
    # UDP扫描模式，不传入参数的话，可以使用action='store_true'，如：当传入-U时，args.udp=True
    parser.add_argument('-U', dest='udp', help='Use the UDP to specify the posts', action='store_true')
    parser.add_argument('-log', dest='log', help='log the information about the scan result', action='store_true')
    # 创建一个子解析器
    sub_parser = parser.add_subparsers(help='Choose the mode which you want to use')
    # 端口扫描模式一--指定端口扫描
    parser_port = sub_parser.add_parser('port', help='specify target port(s) which you input')
    # 加入nargs='*'匹配多个参数，生成一个列表
    parser_port.add_argument('port', help='specify target port(s)', nargs='*')
    # 端口扫描模式二--端口范围扫描
    parser_range_port = sub_parser.add_parser('port_range', help='specify target port(s) in the range')
    # 指定了nargs=1，args.x、args.y变为列表形式
    parser_range_port.add_argument('x', type=str, nargs=1, help='Scan the ports from the num of x')
    parser_range_port.add_argument('y', type=int, nargs=1, help='stop the Scanner until to the num of y')
    # 端口扫描模式三--扫描知名端口
    parser_known_port = sub_parser.add_parser('port_known', help='specify target port(s) known')
    parser_known_port.add_argument('port_known', action='store_true')
    # 绑定自定义的函数
    parser.set_defaults(func=range_port)
    parser.set_defaults(func1=deal_tgthost)
    parser.set_defaults(func2=deal_tgtport)
    args = parser.parse_args()
    return args


class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


def main():
    args = deal_argument()
    # 输出信息记录到文件中
    if args.log:
        sys.stdout = Logger("log.txt")
    print datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 对传入的主机信息进行处理
    tgthost = args.func1(args)
    mode = '0'
    if args.udp:
        mode = '1'
    # 检查args的对象，选择不同的端口扫描模式
    if hasattr(args, 'port'):
        tgtport = args.func2(args)
        if (tgthost == None or len(tgtport) == 0):
            print '[-] You must specify a target host and ports'
            exit(0)
        portscan(tgthost, tgtport, mode)
    elif hasattr(args, 'x') and hasattr(args, 'y'):
        if args.tgthost is not None:
            # 调用外部自定义的函数
            args.func(tgthost, args, mode)
    elif hasattr(args, 'port_known'):
        if args.udp:
            tgtport_known = ['7', '53', '67', '69', '161', '162']
        else:
            tgtport_known = ['20', '21', '22', '23', '25', '53', '80', '110', '443']
        portscan(tgthost, tgtport_known, mode)


if __name__ == '__main__':
    main()