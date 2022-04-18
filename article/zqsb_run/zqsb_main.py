import zqsb_index
import zqsb_home
import time

# 定时任务
while True:
    zqsb_index.main()
    time.sleep(1)
    zqsb_home.main()
    print(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()))
    time.sleep(30)