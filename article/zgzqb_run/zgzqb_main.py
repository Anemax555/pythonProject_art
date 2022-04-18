import zgzqb_index
import zgzqb_rss
import zgzqb_home
import zqzqb_epaper_rss
import time

# 定时任务
while True:
    zqzqb_epaper_rss.main()
    time.sleep(1)
    zgzqb_rss.main()
    time.sleep(1)
    zgzqb_index.main()
    time.sleep(1)
    zgzqb_home.main()
    print(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()))
    time.sleep(30)