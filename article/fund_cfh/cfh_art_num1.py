import asyncio
import re
import time
import aiohttp
import pymysql
import os.path
import urllib.request
from redis import StrictRedis
from hashlib import md5

import requests
from lxml import etree


def input_mysql(params):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()

def input_redis(url_id):
    redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    secret = md5()
    secret.update(url_id.encode())
    urlid = secret.hexdigest()
    if not redis.sismember('urllist', urlid):
        redis.sadd('urllist', urlid)


async def get_requests(url):
    async with aiohttp.ClientSession() as sess:
        async with await sess.get(url=url) as resp:
            page_text = await resp.text()
            if (resp.status != 200):
                print("Erro:  ", resp.status, url)
                page = {"url": url, "page": page_text, "status": resp.status}
                return page
            page = {"url": url, "page": page_text, "status": resp.status}
            return page


def article_get(t):
    page = t.result()
    if (page["status"] != 200):
        return
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    page_text = page["page"]
    url = page["url"]
    # print(url)
    tree = etree.HTML(page_text)
    # ================================标题
    title = tree.xpath('//div[@class="article-head"]/h1/text()')
    if (len(title) == 0):
        print('Erro: ',url)
        return
    title = ''.join(title)
    # ================================文章ID
    uid = str(url).split('/')[-1].strip('.html')
    # ================================文章来源
    source = tree.xpath('//div[@class="article-meta"]/span[@id="authorwrap"]/a/text()')
    source = ''.join(source)
    # ================================日期
    sourTime = tree.xpath('//div[@class="article-meta"]/span[@class="txt"]/text()')
    sourTime = ''.join(sourTime)
    # ================================正文
    # context = tree.xpath('//div[@class="article-body"]/div[@class="xeditor_content"]')
    context = tree.xpath('//div[@class="article-body"]')
    if (len(context) == 0):
        print('Erro: ',url)
        return
    if len(context)>0:
        art = etree.tostring(context[0], encoding="utf-8").decode("utf-8")
        art = str(art).strip()
    else:
        art = ""
    # ================================图片
    img_url = tree.xpath('//div[@class="article-body"]/div[@class="xeditor_content"]//img/@src')

    img_list = []
    img_path = "/home/NRGLXT/source/media/img/"
    # img_path = "D:\pythonProject\Pic\\"
    if not os.path.exists(img_path):  # 创建路径
        os.mkdir(img_path)
    for i in range(0, len(img_url)):
        resp = requests.get(img_url[i])
        img_type = resp.headers['Content-Type'].split('/')[-1].strip()
        imgfname = f_inputTime[0:10] + uid + "_" + str(i) + '.' + img_type
        urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)  # 下载图片
        art = art.replace(img_url[i], "http://hzlaiqian.com/media/img/" + imgfname)
        img_list.append("http://hzlaiqian.com/media/img/" + imgfname)
    img_list = ','.join(img_list)
    params = (uid, title, art, source, sourTime, url, f_inputTime, img_list, source)
    input_mysql(params)
    input_redis(url)
    # print(params)


def page_index_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        task.add_done_callback(article_get)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


# url = ['https://caifuhao.eastmoney.com/news/20220508210054942412740']
# page_index_get(url)
