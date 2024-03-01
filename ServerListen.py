import threading
import socket
import time


encoding = 'utf-8'
BUFSIZE = 1024
Host = "192.168.18.14"
Host = "192.168.0.114"

##读取端口消息
class Reader(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        """接收字节消息"""
        while True:
            data = self.client.recv(BUFSIZE)
            if (data):
                timeline = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                content = timeline + "," + bytes.decode(data, encoding) + "\n"
                with open('collecting_data.csv', 'a') as file:
                    print(data)
                    file.write(content)
            else:
                break


class Listener(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(0)

    def run(self):
        """建立端口监听"""
        print("listener started")
        while True:
            client, cltadd = self.sock.accept()
            Reader(client).start()
            cltadd = cltadd


lst = Listener(1234)
lst.start()