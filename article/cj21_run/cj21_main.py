import cj21_index
import cj21web_home
import cj21web_index
import time


# 定时任务
while True:
    cj21_index.main()
    time.sleep(1)
    cj21web_index.main()
    time.sleep(1)
    cj21web_home.main()
    print(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()))
    time.sleep(30)