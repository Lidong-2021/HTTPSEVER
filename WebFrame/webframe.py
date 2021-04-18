"""
web frame.py 模拟后端应用工作流程
从 http server 接收具体请求
根据请求进行逻辑处理和数据处理
将需要的数据反馈给httpserver
"""
from socket import *
import json
from settings import *
from select import select


# 应用类，处理某一方面的请求
class Application:
    def __init__(self):
        self.rlist = []
        self.wlist = []
        self.xlist = []

        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)
        self.sockfd.bind((frame_ip, frame_port))

    def start(self):
        self.sockfd.listen(5)
        print('start app listen %s' % frame_port)
        self.rlist.append(self.sockfd)
        # select 请求监控
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sockfd:
                    connfd, addr = r.accept()
                    self.rlist.append(connfd)
                else:
                    self.handle(r)
                    self.rlist.remove(r)

    # 获取具体网页数据
    def get_html(self, info):
        if info == '/':
            fd = open('index.html', 'r', encoding='utf-8')
            data = fd.read()
            response = {'status': '200', 'data': data}
            return response
        else:
            return {'status': '404', 'data': '404'}

    # 处理具体的 httpserver 请求
    def handle(self, connfd):
        request = connfd.recv(1024).decode()
        request = json.loads(request)
        print(request)
        if request['method'] == 'GET':
            if request['info'] == '/' or request['info'][-5:] == '.html':
                response = self.get_html(request['info'])
            else:
                response = {'status': '404', 'data': '404'}
        elif request['method'] == 'POST':
            response = {'status': '404', 'data': '404'}
        else:
            response = {'status': '404', 'data': '404'}
        # 将数据发送给httpserver
        # response => {'status': '200', 'data': 'xxxxxx'}
        response = json.dumps(response)
        connfd.send(response.encode())
        connfd.close()


app = Application()

app.start()  # 启动应用服务
