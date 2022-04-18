import asyncio
import html
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
        page_text = page["page"]
        url = page["url"]
        tree = etree.HTML(page_text)
        title = tree.xpath('//div[@class="g-article"]/div[@class="g-article-top"]/h1/text()')
        if (len(title) == 0):
            print('版面预警 ', url)
            return
        source = tree.xpath('//div[@class="g-article"]/div[@class="g-article-top"]/p/span[@class="source"]/text()')
        sourceTime = tree.xpath('//div[@class="g-article"]/div[@class="g-article-top"]/p/span[@class="time"]/text()')
        title = str(title[-1]).strip() if len(title) > 0 else ""
        source = str(source[0]).strip() if len(source) > 0 else ""
        sourTime = str(sourceTime[0]).strip() if len(sourceTime) > 0 else ""

        context_zz = re.compile(r'<div class="g-articl-text">(?P<context>.*?)</div>', re.S)
        for it in context_zz.finditer(page_text):
            art = it.group("context").strip()

        # uid = tree.xpath('//div[@class="m-article-like"]/a[@class="f-like likess"]/@article-id')
        uid = str(url).split('/')[-1].strip('.html')

        if ('每经头条（nbdtoutiao）——' in art):
            art = ''.join(art.split('每经头条（nbdtoutiao）——')[0])

        art_path = etree.HTML(art)
        art = html.unescape(art)
        img_url = art_path.xpath('//img/@src')
        img_list = ""
        img_path = "/home/NRGLXT/source/media/img/"
        # img_path = "D:\pythonProject\Pic\\"
        if not os.path.exists(img_path):  # 创建路径
            os.mkdir(img_path)
        for i in range(0, len(img_url)):
            if (str(img_url[i]).split('.')[-1].lower() not in 'bmp，jpg，png，tif，gif，pcx，tga，exif，fpx，svg，psd，cdr，pcd，dxf，ufo，eps，ai，raw，WMF，webp，avif，apng'):
                imgfname = sourTime[0:10] + uid + "_" + str(i) + '.jpg'
                print(html.unescape(img_url[i]))
            else:
                imgfname = sourTime[0:10] + uid + "_" + str(i) + os.path.splitext(img_url[i])[1]
            # urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)  # 下载图片
            art = art.replace(img_url[i], "http://hzlaiqian.com/media/img/" + imgfname)
            img_list = img_list + "http://hzlaiqian.com/media/img/" + imgfname + ","
        f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        params = (uid, title, art, source, sourTime, url, f_inputTime, img_list, "每日经济新闻")
        input_mysql(params)
        # print(params)
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


# url = ['http://www.nbd.com.cn/articles/2022-07-05/2352602.html']
# page_index_get(url)
