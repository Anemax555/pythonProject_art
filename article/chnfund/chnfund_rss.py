import json
import requests
import time
import os.path
import pymysql
import urllib.request
from datetime import datetime
from threading import Timer
from hashlib import md5
from redis import StrictRedis
from lxml import etree


def input_redis(url_id):
    redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis.sismember('urllist', url_id):
        return True
    else:
        redis.sadd('urllist', url_id)
        return False


def input_mysql(params):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite,f_fromurl) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


def get_data_news(data):
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    f_id = data["id"]
    f_title = data["title"]
    f_content = data["content"]
    f_source = data["source"]
    f_sourceTime = data["pubDate"]
    f_url = data["url"]

    art = etree.HTML(f_content)
    img_list = art.xpath('//img/@src')

    mon = time.strftime("%Y-%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    img_path = f"/home/NRGLXT/source/media/img/{mon}/{day}/"
    # img_path = "D:\pythonProject\Pic\\"
    if not os.path.exists(img_path):  # 创建路径
        os.mkdir(img_path)
    img_url = []
    for i in range(0, len(img_list)):
        imgfname = f_id + "_" + str(i) + os.path.splitext(img_list[i])[1]
        url1 = f"http://hzlaiqian.com/media/img/{mon}/{day}/" + imgfname
        f_content = f_content.replace(img_list[i], url1)
        urllib.request.urlretrieve(img_list[i], filename=img_path + imgfname)  # 下载图片
        img_url.append(url1)
    img_url = json.dumps(img_url)

    params = (f_id, f_title, f_content, f_source, f_sourceTime, f_url, f_inputTime, img_url, "中国基金报", "中国基金报RSS")
    input_mysql(params)
    # print(params)
    # print(img_url)


def get_data_news_list(url):
    resp = requests.get(url)
    data_json = json.loads(resp.text)

    secret = md5()
    num = 0
    for i in range(len(data_json)):
        f_id = data_json[i]["id"]
        secret.update(f_id.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            num = num + 1
            get_data_news(data_json[i])
    print(f"中国基金报更新：{num}条数据")


def main():
    url = 'https://www.chnfund.com/content/list'
    get_data_news_list(url)


def task():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def timedTask():
    '''
    第一个参数: 延迟多长时间执行任务(秒)
    第二个参数: 要执行的函数
    第三个参数: 调用函数的参数(tuple)
    '''
    Timer(5, main, ()).start()


while True:
    timedTask()
    time.sleep(30)
