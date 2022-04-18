from datetime import datetime
from threading import Timer
import time


# 定时任务
def task():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def timedTask():
    '''
    第一个参数: 延迟多长时间执行任务(秒)
    第二个参数: 要执行的函数
    第三个参数: 调用函数的参数(tuple)
    '''
    Timer(30, task, ()).start()


while True:

    timedTask()
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    print(f_inputTime)
    time.sleep(5)