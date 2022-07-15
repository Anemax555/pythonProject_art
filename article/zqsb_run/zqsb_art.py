import asyncio
import json
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
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite,f_fromurl) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


async def get_requests(url):
    async with aiohttp.ClientSession() as sess:
        try:
            async with await sess.get(url=url["url"]) as resp:
                page_text = await resp.text()
                if (resp.status != 200):
                    print("Erro:  ", resp.status, url)
                    page = {"url": url, "page": page_text, "status": resp.status}
                    return page
                page = {"url": url, "page": page_text, "status": 200}
                return page
        except:
            print("Erro_link", url)
            page = {"url": url, "page": "", "status": 600}
            return page


def article_get(t):
    try:
        page = t.result()
        f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        if (page["status"] != 200):
            return
        page_home = page["page"]
        url = page["url"]["url"]
        furl = page["url"]["furl"]
        tree = etree.HTML(page_home)
        tit_zz = re.compile(
            r'<div class="intal_tit">.*?<h2>(?P<title>.*?)</h2>.*?<div class="info">(?P<sourceTime>.*?)<span>来源：(?P<source>.*?)</span>',
            re.S)
        news_id = str(url).split('/')[-1].strip('.html')

        tit = tit_zz.finditer(page_home)

        f_title = ''
        for it in tit:
            f_title = re.sub('<[^<]+?>', '', it.group("title")).strip()
            f_sourceTime = re.sub('<[^<]+?>', '', it.group("sourceTime")).strip()
            f_source = re.sub('<[^<]+?>', '', it.group("source")).strip()
        if (len(f_title) == 0):
            f_title = tree.xpath(
                "//div[@class='content clearfix']/div[@class='box_left3']/div[@class='xiangxi']/h2/text()")
            f_title = ''.join(f_title).strip()
            sourceTime_zz = re.compile(r'<div class="xiangxi">.*?<span>(?P<time>.*?)来源', re.S)
            source_zz = re.compile(r'<div class="xiangxi">.*?来源：(?P<source>.*?)</span>', re.S)
            for it in source_zz.finditer(page_home):
                f_source = it.group('source').strip()
            for it in sourceTime_zz.finditer(page_home):
                f_sourceTime = it.group('time').strip()

        if len(f_title) == 0:
            print("版面异常：", url)
            return
        f_context_zz = re.compile(r'<div class="txt_con" id="ctrlfscont".*?>(?P<context>.*?)<div class="fenxiang">',
                                  re.S)
        f_zy_1_zz = re.compile(r'<script.*?</script>', re.S)

        f_context = ""
        for it in f_context_zz.finditer(page_home):
            f_context = it.group('context').strip()
        f_zy_1 = f_zy_1_zz.findall(f_context)
        # print(f_zy_1)

        for i in range(len(f_zy_1)):
            f_context = f_context.replace(f_zy_1[i], '')

        content = etree.HTML(f_context)
        img_url = content.xpath('//img/@src')
        mon = time.strftime("%Y-%m", time.localtime())
        day = time.strftime("%d", time.localtime())

        img_path = f'/home/NRGLXT/source/media/img/{mon}/{day}/'
        # img_path = "D:\pythonProject\Pic\\"
        if not os.path.exists(img_path):  # 创建路径
            os.mkdir(img_path)
        img_list = []

        for i in range(0, len(img_url)):
            imgfname = news_id + '_' + str(i) + os.path.splitext(img_url[i])[1]
            url1 = f'http://hzlaiqian.com/media/img/{mon}/{day}/' + imgfname
            f_context = f_context.replace(img_url[i], url1)
            if ("http" not in img_url[i]):
                img_url[i] = url.replace(url.split('/')[-1], img_url[i].strip('.'))
            urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)  # 下载图片
            img_list.append(url1)
        img_list = json.dumps(img_list)
        params = (news_id, f_title, f_context, f_source, f_sourceTime, url, f_inputTime, img_list, "证券时报", furl)
        # print(params)
        input_mysql(params)
    except:
        print("Erro ", url)


def page_index_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        task.add_done_callback(article_get)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

# url = [{'furl':'111','url':'https://news.stcn.com/news/202207/t20220714_4739021.html'}]
# page_index_get(url)
