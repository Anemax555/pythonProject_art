import asyncio
import json
import re
import aiohttp
import time
import urllib.request
import pymysql
import os.path
from lxml import etree
from redis import StrictRedis
from hashlib import md5

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"}


def input_mysql(params):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite,f_fromurl) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


async def get_requests(url):
    async with aiohttp.ClientSession() as sess:
        async with await sess.get(url=url["url"]) as resp:
            if (resp.status != 200):
                print("Erro:  ", resp.status, url)
            page_text = await resp.text("gbk", "ignore")
            page = {"url": url, "page": page_text}
            return page


def wx_get(t):
    # try:
        page = t.result()
        page_text = page["page"]
        url = page["url"]["url"]
        furl = page["url"]["furl"]
        page_html = etree.HTML(page_text)
        uid = str(url).split('/')[-1].split('.')[0].strip()
        title = page_html.xpath('//h1/text()')
        title = str(title[0]).strip() if (len(title) > 0) else ""
        context_zz = re.compile(r'<div class="rich_media_content.*?">(?P<context>.*?)</section>', re.S)
        context = ""
        for it in context_zz.finditer(page_text):
            context = it.group("context")
        art = page_html.xpath('//div[@id="js_content"]')
        source = page_html.xpath('//strong[@class="profile_nickname"]/text()')
        source = str(source[0]).strip() if len(source) > 0 else ""
        sourTime = time.strftime("%Y-%m-%d", time.localtime())
        content = etree.HTML(context)

        mon = time.strftime("%Y-%m", time.localtime())
        day = time.strftime("%d", time.localtime())
        # img_url = content.xpath('//img/@data-src')
        # print(context)

        for i in range(len(art)):
            print(etree.tostring(art[i],encoding='', method="html").decode())
        # img_type = content.xpath('//img/@data-type')
        # img_path = f'/home/NRGLXT/source/media/img/{mon}/{day}/'
        # # img_path = "D:\pythonProject\Pic\\"
        # img_list = []
        # if not os.path.exists(img_path):
        #     os.mkdir(img_path)
        # for i in range(0, len(img_url)):
        #     imgfname = uid + "_" + str(i) + "." + str(img_type[i])
        #     urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)
        #     url1 = f'http://hzlaiqian.com/media/img/{mon}/{day}/' + imgfname
        #     context = context.replace(img_url[i], url1)
        #     img_list.append(img_url)
        # img_list = json.dumps(img_list)
        # f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        # params = (uid, title, context, source, sourTime, url, f_inputTime, img_list, "中国证券报", furl)
        # # input_mysql(params)
        # print(params)
        # print(img_list)
    # except:
    #     print("Erro ", url)


def article_get(t):
    try:
        page = t.result()
        page_text = page["page"]
        url = page["url"]["url"]
        furl = page["url"]["furl"]
        page_html = etree.HTML(page_text)
        uid = str(url).split('_')[-1].split('.')[0].strip()
        title = page_html.xpath('//h1/text()')
        title = str(title[0]).strip() if (len(title) > 0) else ""
        # art = etree.tostring(page_html.xpath('//article[@class="cont_article"]'))
        art_zz = re.compile(r'<article class="cont_article">.*?<section>(?P<context>.*?)<script', re.S)
        context = ""
        for it in art_zz.finditer(page_text):
            context = it.group("context").strip()
        art = etree.HTML(context)
        source = page_html.xpath('//div[@class="artc_info"]/div/em[2]/text()')
        source = ''.join(source).strip()
        sourTime = page_html.xpath('//div[@class="artc_info"]/div/time/text()')
        sourTime = str(sourTime[0]).strip() if len(sourTime) > 0 else ""

        img_url = art.xpath('//img/@src')
        mon = time.strftime("%Y-%m", time.localtime())
        day = time.strftime("%d", time.localtime())

        img_list = []
        img_path = f'/home/NRGLXT/source/media/img/{mon}/{day}/'
        # img_path = "D:\pythonProject\Pic\\"
        if not os.path.exists(img_path):  # 创建路径
            os.mkdir(img_path)

        for i in range(0, len(img_url)):
            imgfname = uid + "_" + str(i) + os.path.splitext(img_url[i])[1]
            url1 = f'http://hzlaiqian.com/media/img/{mon}/{day}/' + imgfname
            context = context.replace(img_url[i], url1)
            if ("http" not in img_url[i]):
                img_url[i] = url.replace(url.split('/')[-1], img_url[i].strip('.'))
            urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)  # 下载图片
            img_list.append(url1)
        f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        img_list = json.dumps(img_list)
        params = (uid, title, context, source, sourTime, url, f_inputTime, img_list, "中国证券报", furl)
        input_mysql(params)
        # print(params)
    except:
        print("Erro ", url)


def page_news_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        newurl = str(url).strip()
        if (newurl.find("weixin") != -1):
            task.add_done_callback(wx_get)
            tasks.append(task)
        if (newurl.find("weixin") == -1):
            task.add_done_callback(article_get)
            tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
url = [{'furl': 'https://www.cs.com.cn/', 'url': 'https://mp.weixin.qq.com/s/4iIZx8Xwb5joiRmKeZc39w'}]
page_news_get(url)
