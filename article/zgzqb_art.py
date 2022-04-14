import asyncio
import re
import aiohttp
import time
import urllib.request
import pymysql
import os.path
from lxml import etree

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"}


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
            if (resp.status != 200):
                print("Erro:  ",resp.status,url)
            page_text = await resp.text()
            page = {"url": url, "page": page_text}
            return page


def wx_get(t):
    page = t.result()
    page_text = page["page"]
    url = page["url"]
    page_html = etree.HTML(page_text)
    uid = str(url).split('/')[-1].split('.')[0].strip()
    title = page_html.xpath('//h1/text()')
    title = str(title[0]).strip() if (len(title) > 0) else ""
    context_zz = re.compile(r'<section style="box-sizing: border-box;">(?P<context>.*?)</section>',re.S)
    context = ""
    for it in context_zz.finditer(page_text):
        context = it.group("context")
    art = page_html.xpath('//div[@id="js_content"]//p/text()')
    source = page_html.xpath('//strong[@class="profile_nickname"]/text()')
    source = str(source[0]).strip() if len(source) > 0 else ""
    sourTime = time.strftime("%Y-%m-%d", time.localtime())

    img_url = page_html.xpath('//div[@id="js_content"]//img/@data-src')
    img_type = page_html.xpath('//div[@id="js_content"]//img/@data-type')
    img_path = "/home/NRGLXT/source/media/img/"
    # img_path = "D:\pythonProject\Pic\\"
    img_list = ""
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    for i in range(0, len(img_url)):
        imgfname = sourTime[0:10] + uid + "_" + str(i) + "." + str(img_type[i])
        urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)
        context = context.replace(img_url[i], "http://hzlaiqian.com/media/img/" + imgfname)
        img_list = img_list + "http://hzlaiqian.com/media/img/" + imgfname + ","
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    params = (uid, title, context, source, sourTime, url, f_inputTime, img_list, "中国证券报")
    input_mysql(params)


def article_get(t):
    page = t.result()
    page_text = page["page"]
    url = page["url"]
    page_html = etree.HTML(page_text)
    uid = str(url).split('_')[-1].split('.')[0].strip()
    title = page_html.xpath('//h1/text()')
    title = str(title[0]).strip() if (len(title)>0) else ""
    # art = etree.tostring(page_html.xpath('//article[@class="cont_article"]'))
    art_zz = re.compile(r'<article class="cont_article">.*?<section>(?P<context>.*?)</section>',re.S)
    context = ""
    for it in art_zz.finditer(page_text):
        context = it.group("context").strip()
    art = etree.HTML(context)
    source = page_html.xpath('//div[@class="artc_info"]/div/em/text()')
    source = str(source[1]).strip() if len(source)>0 else ""
    sourTime = page_html.xpath('//div[@class="artc_info"]/div/time/text()')
    sourTime = str(sourTime[0]).strip() if len(sourTime)>0 else ""

    img_url = art.xpath('//img/@src')

    img_list = ""
    img_path = "/home/NRGLXT/source/media/img/"
    # img_path = "D:\pythonProject\Pic\\"
    if not os.path.exists(img_path): #创建路径
        os.mkdir(img_path)

    for i in range(0, len(img_url)):
        imgfname = sourTime[0:10] + uid + "_" + str(i) + os.path.splitext(img_url[i])[1]
        if ("http" not in img_url[i]):
            img_url = url.replace(url.split('/')[-1], img_url[i].strip('.'))
        urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname) #下载图片
        context = context.replace(img_url[i], "http://hzlaiqian.com/media/img/" + imgfname)
        img_list = img_list + "http://hzlaiqian.com/media/img/" + imgfname + ","
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    params = (uid, title, context, source, sourTime, url, f_inputTime, img_list, "中国证券报")
    input_mysql(params)


def page_news_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        newurl = str(url).strip()
        if (newurl.find("weixin") != -1):
            task.add_done_callback(wx_get)
            tasks.append(task)
            print("wx:",url)
        if (newurl.find("weixin")== -1):
            task.add_done_callback(article_get)
            tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
url = ['https://www.cs.com.cn/sylm/jsbd/202204/t20220412_6259071.html']
page_news_get(url)