import paramiko
import time


def disable_paging(remote_conn):
    '''Disable paging on a Cisco router'''

    remote_conn.send("terminal length 0\n")
    time.sleep(1)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output


if __name__ == '__main__':


    # VARIABLES THAT NEED CHANGED
    ip = '192.168.200.50'
    username = 'cisco'
    password = '!cisco123!'

    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(
         paramiko.AutoAddPolicy())

    # initiate SSH connection
    #remote_conn_pre.connect(ip, username=username, password=password)
    #remote_conn_pre.connect(pkey='/home/cisco/.ssh/id_dsa.pub',username='cisco')

    remote_conn_pre.connect('192.168.200.31',username='cisco',password='cisco',port=7001)
    #print "SSH connection established to %s" % ip

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    print "Interactive SSH session established"

    # Strip the initial router prompt
    output = remote_conn.recv(2000)

    # See what we have
    print output

    # Turn off paging
    #disable_paging(remote_conn)

    # Now let's try to send the router a command
    remote_conn.send("\n")
    output = remote_conn.recv(10000)

    # See what we have
    print output
    time.sleep(.4)
    remote_conn.send("cisco\n")
    time.sleep(.4)
    remote_conn.send("!cisco123!\n")
    time.sleep(.6)
    print 'Logged into Cisco Switch'
    output = remote_conn.recv(10000)
    time.sleep(2)
    print output
    print 'testing'
    time.sleep(1)
    remote_conn.send("show ip int brief\n")
    time.sleep(1)
    output = remote_conn.recv(6000)
    time.sleep(1)
    print output
    time .sleep(1)
    remote_conn.send('show cdp neighbor\n')
    time.sleep(1)
    output = remote_conn.recv(8000)
    time.sleep(1)
    print output
    time.sleep(1)
    remote_conn.send("exit\n")
    time.sleep(1)
