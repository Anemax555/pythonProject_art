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
        async with await sess.get(url=url["url"]) as resp:
            page_text = await resp.text()
            if (resp.status != 200):
                print("Erro:  ", resp.status, url)
                page = {"url": url, "page": page_text, "status": resp.status}
                return page
            page = {"url": url, "page": page_text, "status": 200}
            return page


def article_get(t):
    page = t.result()
    if (page["status"] != 200):
        return
    try:
        page_text = page["page"]
        url = page["url"]["url"]
        furl = page["url"]["furl"]
        f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        tree = etree.HTML(page_text)
        uid = str(url).split('/')[-1].strip('.html')
        title = tree.xpath('//div[@class="titleHead"]//h1/text()')
        context_zz = re.compile(r'<div class="main_content">(?P<context>.*?)</div>', re.S)
        source = tree.xpath('//div[@class="titleHead"]//div[@class="newsInfo"]/text()')
        sourTime = tree.xpath('//div[@class="titleHead"]//div[@class="newsDate"]/text()')
        img_url = tree.xpath('//div[@class="main_content"]//img/@data-original')

        if (len(title) > 0):
            title = ''.join(title).strip()
        else:
            print("版面格式警报", "21财经", url)
            return

        if (len(source) == 0):
            source = tree.xpath('//div[@class="author-infos"]//b/text()')
            sourTime = tree.xpath('//div[@class="author-infos"]//span/text()')[0]
            sourTime = str(sourTime).split(' ')[-2] + ' ' + str(sourTime).split(' ')[-1]
        if (len(source) == 0):
            source = tree.xpath('//div[@class="author-infos"]/text()')
        if (len(source) == 0):
            source = tree.xpath('//div[@class="author-infos"]/a/text()')
        source = str(source[0]).strip()
        f_source = source.split(' ')[0]
        if ("21财经APP" in source):
            f_source = f_source + ' ' + source.split(' ')[1]
        art = ""
        for it in context_zz.finditer(page_text):
            art = it.group("context")
        art.strip()

        type_list = ['bmp', 'jpg', 'png', 'tif', 'gif', 'pcx', 'tga', 'exif', 'fpx', 'svg', 'psd', 'cdr', 'pcd', 'dxf',
                     'ufo', 'eps', 'ai', 'raw', 'wmf', 'webp', 'avif', 'apng','jpeg']

        #======================================图片
        mon = time.strftime("%Y-%m", time.localtime())
        day = time.strftime("%d", time.localtime())
        img_list = []
        img_path = f"/home/NRGLXT/source/media/img/{mon}/{day}/"
        # img_path = "D:\pythonProject\Pic\\"
        if not os.path.exists(img_path):  # 创建路径
            os.mkdir(img_path)
        for i in range(0, len(img_url)):
            url_type = os.path.splitext(img_url[i])[1]
            for j in range(len(type_list)):
                if type_list[j] in url_type:
                    url_type = type_list[j]
            imgfname = uid + "_" + str(i) + '.' + url_type
            url1 = f"http://hzlaiqian.com/media/img/{mon}/{day}/" + imgfname
            urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)  # 下载图片
            art = art.replace(img_url[i], url1)
            img_list.append(url1)
        img_list= json.dumps(img_list)
        params = (uid, title, art, f_source, sourTime, url, f_inputTime, img_list, "21世纪经济报道", furl)
        input_mysql(params)

        #======================================================test

        # params = (uid, title, f_source, sourTime, url, f_inputTime, img_list, "21世纪经济报道")
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


# url = [{'furl': 'http://m.21jingji.com/','url': 'https://m.21jingji.com/article/20220711/herald/3c2fb6c8be24b28f46060bf45ce381e0.html'}]
# page_index_get(url)
