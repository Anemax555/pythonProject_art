import asyncio
import re
import time
import aiohttp
import pymysql
import os.path
import urllib.request
from lxml import etree


def input_mysql(params):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


async def get_requests(url):
    async with aiohttp.ClientSession() as sess:
        async with await sess.get(url=url) as resp:
            page_text = await resp.text()
            if (resp.status != 200):
                print("Erro:  ", resp.status, url)
                page = {"url": url, "page": page_text, "status": 403}
                return page
            page = {"url": url, "page": page_text, "status": 200}
            return page


def article_get(t):
    try:
        page = t.result()
        if (page["status"] != 200):
            return
        page_home = page["page"]
        url = page["url"]
        news_content_zz = re.compile(
            r'<div class="news_content">.*?<h1>(?P<title>.*?)</h1>.*?<div class="info_news">(?P<sourceTime>.*?)来源：(?P<source>.*?)</div>.*?<!--con-->(?P<context>.*?)<!--end-->',
            re.S)
        news_id_zz = re.compile(r'encodeURIComponent.*?title_id=(?P<news_id>.*?)&title.*?</html>', re.S)
        img_url_zz = re.compile(r'<img src="(?P<imgurl>.*?)"', re.S)

        for i in news_id_zz.finditer(page_home):
            news_id = i.group("news_id")

        news_content = news_content_zz.finditer(page_home)
        for it in news_content:
            f_title = re.sub('<[^<]+?>', '', it.group("title")).strip()
            f_context = it.group("context").strip()
            f_source = re.sub('<[^<]+?>', '', it.group("source")).strip()
            f_sourceTime = re.sub('<[^<]+?>', '', it.group("sourceTime")).strip()
            f_sourceAddress = url
            f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
            imgurls = img_url_zz.findall(it.group())
            imgurls_list = ""
            if (len(imgurls) > 0):
                for i in range(0, len(imgurls)):
                    if (imgurls[i].find("http") != -1):
                        imgfname = f_sourceTime[0:10] + news_id + "_" + str(i) + os.path.splitext(imgurls[i])[1]
                        img_path = "/home/NRGLXT/source/media/img/"
                        if not os.path.exists(img_path):
                            os.mkdir(img_path)
                        #urllib.request.urlretrieve(imgurls[i], filename=img_path + imgfname)
                        f_context = f_context.replace(imgurls[i], "http://hzlaiqian.com/media/img/" + imgfname)
                        imgurls_list = imgurls_list + "http://hzlaiqian.com/media/img/" + imgfname + ','

            params = (news_id, f_title, f_context, f_source, f_sourceTime, f_sourceAddress, f_inputTime, imgurls_list, "证券日报")
            input_mysql(params)
    except:
        print("Erro ",url)


def page_index_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        task.add_done_callback(article_get)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
#
# url = ['http://www.nbd.com.cn/articles/2019-11-06/1384228.html']
# page_index_get(url)
