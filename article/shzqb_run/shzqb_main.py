import shzqb_index
import time

# 定时任务
while True:
    shzqb_index.main()
    print(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()))
    time.sleep(30)