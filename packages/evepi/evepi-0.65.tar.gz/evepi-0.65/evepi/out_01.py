#coding=utf-8
import socket
import json

fuck_json_path = open( "/etc/out_01/fuckpath.md" ).read()
fuck_json_file = file( fuck_json_path )
fuck_json = json.load( fuck_json_file )

def input_cmd_string( name, cmd="fuck" ):
    # fuck the cmd to the machine via socket
    global fuck_json
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # 定义socket类型，网络通信
    s.connect( (fuck_json[name][0], fuck_json[name][1]) )       # 要连接的IP与端口
    s.sendall( cmd )      # 把命令发送给对端
    data=s.recv(1024)     # 把接收的数据定义为变量
    s.close()   # 关闭连接
    return data

def get_input_string( name, cursor_whether, cursor_j=0, cursor_i=0, input_string="" ):
    # 生成json格式字符串命令
    json_dict = { "cursor_whether": cursor_whether, \
                  "cursor_j": cursor_j, \
                  "cursor_i": cursor_i, \
                  "input_string": input_string }
    json_dict = json.dumps( json_dict )
    return input_cmd_string( name, json_dict )

def clear( name ):
    # 清空并把光标移动到原点
    return get_input_string( name, 2 )

def set_cursor( name, cursor_j, cursor_i ):
    # only set cursor
    return get_input_string( name, 1, cursor_j=cursor_j, cursor_i=cursor_i )

def print_it( name, input_string ):
    # only print it
    return get_input_string( name, 0, input_string=input_string )