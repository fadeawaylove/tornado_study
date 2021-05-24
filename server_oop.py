# 用面向对象的方式改写

from select import select
from socket import socket, AF_INET, SOCK_STREAM
from collections import deque


class Scheduler:

    def __init__(self):
        self._ready = deque()  # 准备运行的任务
        self._read_waiting = {}  # 读等待的任务,key为fileno
        self._write_waiting = {}  # 写等待的任务,key为fileno

    def new(self, task):
        """
        新增一个task到ready队列中(初始化,msg=None)
        :param task:
        :return:
        """
        self._ready.append((task, None))

    def add_ready(self, task, msg=None):
        """
        添加一个task到ready队列中
        :param task:
        :param msg:
        :return:
        """
        self._ready.append((task, msg))


class Socket(object):
    pass


def server():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("", 18181))
    server_socket.listen(10)

    r_list = [server_socket]
    w_list = []
    message_queues = {}
    while True:
        readable, writeable, exceptions = select(r_list, w_list, r_list)

        for r_so in readable:
            r_so: socket
            if r_so is server_socket:  # 收到连接
                c_so, c_addr = r_so.accept()
                print("connection from %s" % (c_addr,))
                r_list.append(c_so)
                message_queues[c_so] = []
            else:
                msg = r_so.recv(10240)
                if not msg or msg == b'\r\n':  # 结束连接
                    print("closing connection form %s" % (r_so.getpeername(),))
                    if r_so in w_list:
                        w_list.remove(r_so)
                    r_list.remove(r_so)
                    r_so.close()
                    del message_queues[r_so]
                else:  # 收到消息
                    print(f"msg from {r_so.getpeername()}: {msg}")
                    message_queues[r_so].append(msg)
                    if r_so not in w_list:
                        w_list.append(r_so)
        for w_so in writeable:
            w_so: socket
            mq = message_queues[w_so]
            data = b"out: "
            while mq:
                m = mq.pop(0)
                data += m
            w_so.send(data)
            print(f"msf send to {w_so.getpeername()}: {data}")
            w_list.remove(w_so)
            if w_so not in readable:
                readable.append(w_so)


if __name__ == "__main__":
    server()
