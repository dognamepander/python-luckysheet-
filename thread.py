# coding: utf-8
import subprocess
import multiprocessing
import threading
import os ,time
import tkinter as tk
import psutil
import pystray
from pystray import MenuItem as item
from PIL import Image

def main():
    show_window()
    menu = (item('退出', quit_window), item('显示', show_window))
    image = Image.open("1.png")
    icon = pystray.Icon("name", image, "title", menu)
    icon.run()

def quit_window(icon, item):
    subprocess.run(["taskkill", "/im", "app.exe", "/f"])
    subprocess.run(["taskkill", "/im", "exmysql.exe", "/f"])
    icon.stop()

def show_window():
    global var
    window = tk.Tk()
    window.title('在线表格-服务器启动.exe')
    window.geometry('250x100')
    var = tk.StringVar()  # 定义一个字符串变量
    l = tk.Label(window, textvariable=var, bg='green', font=('宋体', 8), width=40, height=5, justify='center').pack()
    tk.Button(window, text='一键启动', width=15, height=2, command=thread1).pack()
    thread3()
    window.mainloop()

def fun1():
    os.system('python ./app.py')
    #os.system('app.exe')
    #subprocess.run('app.exe', shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def fun2():
    os.system('python ./exmysql.py')
    #os.system('exmysql.exe')
    #subprocess.run('exmysql.exe', shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def thread1():
    sing_process = multiprocessing.Process(target=fun1)
    dance_process = multiprocessing.Process(target=fun2)
    sing_process.start()
    dance_process.start()

def is_program_running(program_name):
    for p in psutil.process_iter():
        try:
            if program_name == p.name():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def refresh_window():
    list1 = []
    while True:
        if is_program_running('mysqld.exe'):
            list1.append('mysql已启动')
        else:
            list1.append('mysql未启动')
        if is_program_running('app.exe'):
            list1.append('websocket已启动')
        else:
            list1.append('websocket未启动')
        if is_program_running('exmysql.exe'):
            list1.append('exmysql已启动')
        else:
            list1.append('exmysql未启动')
        var.set(list1)
        list1.clear()
        time.sleep(3)

def thread3():
    thread = threading.Thread(target=refresh_window)
    thread.start()

if __name__ == '__main__':
    multiprocessing.freeze_support() # 窗口不报错
    main()

