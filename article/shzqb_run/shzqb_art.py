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
    # resp = open("test.html",mode='r',encoding='utf-8')
    # page_html = etree.HTML(resp.read())
    # title_zz = re.compile(r'rich_media_title.*?>(?P<title>.*?)</h1>')
    # title = ''
    # for item in title_zz.finditer(page_text):
    #     title = item.group('title').strip()
    title = page_html.xpath("//body[@id='activity-detail']/div[@id='js_article']/div[@class='rich_media_inner']/div[@id='page-content']/div[@class='rich_media_area_primary_inner js_rich_media_area_primary_inner']/div[@id='img-content']/h1[@id='activity-name']/text()")

    if (len(title) == 0):
        print('版面预警：', url)
        return

    title = str(title[0]).strip()

    source = page_html.xpath('//strong[@class="profile_nickname"]/text()')
    author = page_html.xpath('//span[@class="rich_media_meta rich_media_meta_text"]/text()')
    article = page_html.xpath('//div[@id="js_content"]/section/section')[1]
    img_url = article.xpath('//section[2]//img/@data-src')
    img_type = article.xpath('//section[2]//img/@data-type')
    sourTime = time.strftime("%Y-%m-%d", time.localtime())
    uid = str(url).split('/')[-1]
    uid = uid.strip()
    if (len(source) > 0):
        source = str(source[0]).strip()
    else:
        source = ""
    if (len(author) > 0):
        author = str(author[0]).strip()
    else:
        author = ""

    context = ""
    for i in article:
        context = context + str(etree.tostring(i)).strip("b'")

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
    params = (uid, title, context, source, sourTime, url, f_inputTime, img_list, "上海证券报")
    input_mysql(params)
    # print(params)


def article_get(t):
    try:
        page = t.result()
        page_text = page["page"]
        url = page["url"]
        page_html = etree.HTML(page_text)
        article = page_html.xpath('//div[@class="content"]')
        title = page_html.xpath('//div[@class="main-content text-large"]/h1/text()')

        if (len(title) == 0):
            print('版面预警：', url)
            return
        else:
            title = str(title[0]).strip()
        sour = page_html.xpath(
            '//div[@id="pager-content"]//span[@class="source"]//text()')

        author = str(page_html.xpath(
            '//div[@class="main-content text-large"]/div[@class="bullet"]/span[@class="author"]/text()')).strip()
        img_url = page_html.xpath('//div[@class="content"]//img/@src')
        uid = str(page_html.xpath('//div[@class="content"]/input[@id="hid_docId"]/@value')[0]).strip()
        sourTime = page_html.xpath('//div[@class="main-content text-large"]//span[@class="timer"]/text()')[0]
        sourTime = str(sourTime).strip()
        context_zz = re.compile(r'<div class="content" id="qmt_content_div">(?P<context>.*?)<div class="bullet">', re.S)
        for it in context_zz.finditer(page_text):
            context = it.group("context")
        source = ""
        for i in range(len(sour)):
            if ("来源"not in sour[i]):
                source = source + str(sour[i]).strip()
            else:
                source = source + str(sour[i]).replace("来源：","")
        img_list = ""
        img_path = "/home/NRGLXT/source/media/img/"
        # img_path = "D:\pythonProject\Pic\\"
        if not os.path.exists(img_path): #创建路径
            os.mkdir(img_path)

        for i in range(0, len(img_url)):
            imgfname = sourTime[0:10] + uid + "_" + str(i) + os.path.splitext(img_url[i])[1]
            urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname) #下载图片
            context = context.replace(img_url[i], "http://hzlaiqian.com/media/img/" + imgfname)
            img_list = img_list + "http://hzlaiqian.com/media/img/" + imgfname + ","
        f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        params = (uid, title, context, source, sourTime, url, f_inputTime, img_list, "上海证券报")
        input_mysql(params)
        # print(params)
    except:
        print("Erro ",url)


def page_news_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        newurl = str(url).strip()
        if (newurl.find("weixin") != -1):
            task.add_done_callback(wx_get)
            tasks.append(task)
        if (newurl.find("weixin")== -1):
            task.add_done_callback(article_get)
            tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

# url = ['https://news.cnstock.com/news,bwkx-202207-4911917.htm']
# page_news_get(url)