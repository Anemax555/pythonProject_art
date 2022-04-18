import sys
import time
sys.path.append("/home/NRGLXT/pythonproject/project_art/py_projiec_358/")
from operation import eastmoney_index as eastmoey
from operation import ths_index as ths
from operation import sina_index as sina



while True:
    eastmoey.main()
    ths.main()
    sina.main()
    print("===========运营位置")
    time.sleep(80)