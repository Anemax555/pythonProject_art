import shzqb_index
import zgzqb_index
import cj21_index
import zqsb
import zqrb
import time

while True:
    shzqb_index.main()
    zgzqb_index.main()
    zqrb.download_main()
    zqsb.download_main()
    cj21_index.main()
    time.sleep(80)