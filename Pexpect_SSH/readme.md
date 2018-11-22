Use the Pexpect to use SSH. Linux系统中使用！

use_pxssh_SSH1.py和use_pxssh_SSH2.py两个程序可以单独使用也可以一起使用！

### use_pxssh_SSH1.py
> 使用前输入“-h”可查看如何使用

程序介绍：<br>
该程序使用多线程来进行SSH用户名和密码爆破

两种模式：<br>
> 输入参数时，文件不需要带后缀，只需要文件名即可
1. 用户名和密码均使用文件遍历爆破。文件夹中有“user.txt”和“passwd.txt”两个文件，用户可以按照格式输入相应内容进行测试，也可以自己创建新的TXT文件
来进行测试
2. 指定用户名，密码则使用文件来爆破

另外还可以选择参数来生成存储已经爆破成功的主机及其用户名和密码，即文件夹中的“log_ssh.txt”文件，该文件可用于use_pxssh_SSH2.py程序使用，也可根据给出文本格式
来自己增添正确的主机信息用于连接；由于该文件用于use_pxssh_SSH2.py程序，所以文件名尽量不要修改

### use_pxssh_SSH2.py
> 使用前输入**“+h”**来查看如何使用

程序介绍：<br>
该程序使用多线程来进行SSH连接测试以及操控SSH僵尸网络！

三种模式：
1. 自己输入主机及其用户名密码来进行测试
2. 仅仅输入主机，在“log_ssh.txt”文件中寻找是否存在该主机的信息，如存在则直接进行连接，否则直接退出
3. 直接使用“-F”参数来对“log_ssh.txt”文件中的主机全部进行连接

命令输入：<br>
可以使用“++cmd”参数来对连接成功的主机发送命令，配合模式三使用可造成一定的攻击效力，批量操作SSH僵尸网络！