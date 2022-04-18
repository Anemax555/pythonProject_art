import zqrb_index
import zqrb_home
import time

# 定时任务
while True:
    zqrb_index.main()
    time.sleep(1)
    zqrb_home.main()
    print(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()))
    time.sleep(30)