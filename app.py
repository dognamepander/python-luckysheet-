# coding: utf-8
import json
import uuid  # UUID（全称为Universally Unique IDentifier）是128位的全局唯一标识符
import pywss
import zlib
import threading
import pymysql
from urllib.parse import unquote  #解压缩
from flask import Flask, request

class Pool:
    lock = threading.Lock()
    pool = {}

    @classmethod  #Python中的类方法
    def add(cls, uid, ctx):
        with cls.lock:  # with是一种上下文管理协议，包含方法 __enter__() 和 __exit__()
            cls.pool[uid] = ctx

    @classmethod
    def delete(cls, uid):
        with cls.lock:
            cls.pool.pop(uid, None)

    @classmethod
    def notify(cls, data, by):
        with cls.lock:
            for uid, ctx in cls.pool.items():  # type: pywss.Context
                if uid == by:
                    continue
                ctx.ws_write(data)  # websocket写入json的数据

def DataToJson():
    conn = pymysql.Connect(host='127.0.0.1', port=3306, user='root', passwd='zz@123456', charset='utf8', db='unicom')
    #  设置自己的mysql信息
    cur = conn.cursor()
    sql = "select * from testlog"  #  选择具体的数据库db='unicom'下的admin
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    jsonData = []
    for i, cell in enumerate(data):
        for j, value in enumerate(cell):
            result = {}
            result['r'] = int(i)
            result['c'] = int(j)
            result['v'] = str(value)
            jsonData.append(result)
    return (jsonData)
    #  luckysheet的要求导出格式



def load(ctx: pywss.Context):
    jsonData = DataToJson()
    data = json.dumps([
        {
            "name": "sheet",
            "index": "sheet_01",
            "order": 0,
            "status": 1,
            "celldata": jsonData,
        }])  # json.dumps将一个Python数据结构转换为JSON
    # json.dumps()用于将dict类型的数据转成str
    ctx.write(data)  # 写入json的数据

def update(ctx: pywss.Context):
    # 升级 WebSocket(WebSocket 本质基于 HTTP GET 升级实现，Pywss 则通过WebSocketUpgrade完成此处升级)
    err = pywss.WebSocketUpgrade(ctx)  # 获取故障
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)  # 设置响应状态码
        return
    uid = str(uuid.uuid4())  # 当前使用用户
    #print(uid, data)  # 创建日志
    Pool.add(uid, ctx)  #自建的类
    # 协议由HTTP协议升级成WebSocket协议.

    try:
        # 轮询获取消息
        while True:
            data = ctx.ws_read()
            if data == b"rub":  # 心跳检测（心跳包就是客户端定时发送简单的信息给服务器端告诉它我还在而已)
                continue
            data_raw = data.decode().encode('iso-8859-1')  # 转编码
            data_unzip = unquote(zlib.decompress(data_raw, 16).decode())  # 解压缩
            #print(uid ,data_unzip)  # 通过这里记录日志
            json_data = json.loads(data_unzip)  #json.loads()用于将str类型的数据转成dict。
            resp_data = {
                "data": data_unzip,
                "id": uid,
                "returnMessage": "success",
                "status": 0,
                "type": 3,
                "username": uid,
            }
            if json_data.get("t") != "mv":
                resp_data["type"] = 2
            resp = json.dumps(resp_data).encode()
            Pool.notify(resp, uid)
    except:
        pass
    finally:
        ctx.log.warning(f"{uid} exit")
        Pool.delete(uid)

if __name__ == '__main__':
    app = pywss.App()  # 初始化app
    # 注册静态资源
    app.static("/static", ".")
    # 注册 luckysheet 路由
    party = app.party("/luckysheet/api")  # 需访问的地址
    party.post("/loadUrl", load)  # post方式获取网页数据
    party.get("/updateUrl", update)  # Get方式获取网页数据
    # 启动服务
    app.run(host="127.0.0.1", port=8080)  # 启动服务
    #app.run(host="10.33.93.202", port=8080)  # 启动服务