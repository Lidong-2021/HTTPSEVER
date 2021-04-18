"""
http server 部分的主程序
获取 http 请求
将请求发送给 WebFrame
从 web frame 接收反馈数据
将数据组织为 response 格式发送给客户端
"""
from socket import *
import sys
from threading import Thread
from config import *
import re
import json

# 服务器地址
ADDR = (HOST, POST)


# 和web frame 通信的函数
def connect_frame(env):
    s = socket()
    try:
        s.connect((frame_ip, frame_port))
    except Exception as e:
        print(e)
        return
    # 将字典转化为 json
    data = json.dumps(env)
    # 将解析后的请求发送给 web frame
    s.send(data.encode())
    # 接收来自web frame 数据
    data = s.recv(4096 * 100).decode()
    return json.loads(data)


# 将 httpServer 的功能封装为类


class HTTPServer:
    def __init__(self):
        self.address = ADDR
        self.create_socket()  # 和浏览器交互

        self.bind()

    # 创建浏览器交互套接字
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)



    # 绑定地址
    def bind(self):
        self.sockfd.bind(self.address)
        self.ip = self.address[0]
        self.port = self.address[1]

    # 启动服务
    def sever_forever(self):
        self.sockfd.listen(5)
        print('listen the port %d' % self.port)
        while True:
            connfd, addr = self.sockfd.accept()
            print("connect from", addr)
            client = Thread(target=self.handle, args=(connfd,))
            client.setDaemon(True)
            client.start()

    # 具体处理客户端请求任务
    def handle(self, connfd):
        # 获取HTTP请求
        request = connfd.recv(4096).decode()
        pattern = r'(?P<method>[A-Z]+)\s+(?P<info>/\S*)'
        try:
            env = re.match(pattern, request).groupdict()
        except:
            # 客户端断开
            connfd.close()
            return
        else:
            data = connect_frame(env)
            self.response(connfd, data)

    # 给浏览器发送数据
    def response(self, connfd, data):
        # data=》{'status': '200', 'data': 'xxxxxx'}
        if data['status'] == '200':
            responseHeaders = "HTTP/1.1 200 OK\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += '\r\n'
            responseBody = data['data']
        elif data['status'] == '404':
            responseHeaders = "HTTP/1.1 404 NOT Found\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += '\r\n'
            responseBody = data['data']
        else:
            pass
        response_data = responseHeaders + responseBody
        connfd.send(response_data.encode())


httpd = HTTPServer()
httpd.sever_forever()
