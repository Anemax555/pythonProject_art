import time
import cfh_index_num1

# 定时任务
while True:
    cfh_index_num1.main()
    print(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()))
    time.sleep(30)