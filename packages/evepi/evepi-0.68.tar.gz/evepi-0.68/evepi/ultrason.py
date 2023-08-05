#coding=utf-8
import socket
import json
import platform


fuck_json_path_name = "ultrason"



# 判断是否是windows
def whether_is_win():
    if 'indow' in platform.system():
        return True
    else:
        return False

if whether_is_win():
    fuck_json_path_model = "C:\\evepi\\%s\\fuckpath.md"
else:
    fuck_json_path_model = "/etc/%s/fuckpath.md"

fuck_json_path = open( fuck_json_path_model % fuck_json_path_name).read()
fuck_json_file = file( fuck_json_path )
fuck_json = json.load( fuck_json_file )

def get_res( name, cmd="fuck" ):
    global fuck_json
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # 定义socket类型，网络通信
    s.connect( (fuck_json[name][0], fuck_json[name][1]) )       # 要连接的IP与端口
    s.sendall( cmd )      # 把命令发送给对端
    data=s.recv(1024)     # 把接收的数据定义为变量
    s.close()   # 关闭连接
    return data
