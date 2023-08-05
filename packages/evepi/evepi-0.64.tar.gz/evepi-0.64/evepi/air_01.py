#coding=utf-8
import socket
import json

fuck_json_path = open( "/etc/air_01/fuckpath.md" ).read()
fuck_json_file = file( fuck_json_path )
fuck_json = json.load( fuck_json_file )

def get_res( name, cmd="fuck" ):
    global fuck_json
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # 定义socket类型，网络通信
    s.connect( (fuck_json[name][0], fuck_json[name][1]) )       # 要连接的IP与端口
    s.sendall( cmd )      # 把命令发送给对端
    data=s.recv(1024)     # 把接收的数据定义为变量
    s.close()   # 关闭连接
    return int(data)
