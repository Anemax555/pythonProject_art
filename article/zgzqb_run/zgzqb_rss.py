import feedparser
import time
import os.path
import pymysql
import urllib.request
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
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


def get_data_news(data):
    try:
        f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        f_id = str(data["link"]).split('/')[-1].strip('.html')
        f_title = data["title"]
        f_content = data["summary"]
        f_source = '中国证券报中证网 '
        f_sourceTime = data["published"]
        f_url = data["link"]

        art = etree.HTML(f_content)
        img_list = art.xpath('//img/@src')

        img_path = "/home/NRGLXT/source/media/img/"
        # img_path = "D:\pythonProject\Pic\\"
        if not os.path.exists(img_path):  # 创建路径
            os.mkdir(img_path)
        img_url = []
        for i in range(0, len(img_list)):
            imgfname = f_inputTime[0:10] + f_id[-8:] + "_" + str(i) + os.path.splitext(img_list[i])[1]
            f_content = f_content.replace(img_list[i], "http://hzlaiqian.com/media/img/" + imgfname)
            urllib.request.urlretrieve(img_list[i], filename=img_path + imgfname)  # 下载图片
            img_url.append("http://hzlaiqian.com/media/img/" + imgfname)
        img_url = ','.join(img_url)

        params = (f_id, f_title, f_content, f_source, f_sourceTime, f_url, f_inputTime, img_url, "中国证券报·RSS")
        input_mysql(params)
    except:
        print("Erro ",data['link'])



def get_data_news_list(url):
    f_rss = feedparser.parse(url)
    secret = md5()
    num = 0
    for i in range(len(f_rss['entries'])):
        f_url = f_rss['entries'][i]['link']
        secret.update(f_url.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            num = num + 1
            get_data_news(f_rss['entries'][i])
    return num



def main():
    n = get_data_news_list('https://www.cs.com.cn/sylm/jsbd/index_35296.xml')
    print(f"中国证券报·中证网RSS：{n}条数据")
