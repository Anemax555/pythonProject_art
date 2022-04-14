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
    page = t.result()
    if (page["status"] != 200):
        return
    page_text = page["page"]
    url = page["url"]
    tree = etree.HTML(page_text)
    uid = str(url).split('/')[-1].split('.')[0]
    title = tree.xpath('//div[@class="titleHead"]//h1/text()')
    context_zz = re.compile(r'<div class="main_content">(?P<context>.*?)</div>',re.S)
    source = tree.xpath('//div[@class="titleHead"]//div[@class="newsInfo"]/text()')
    sourTime = tree.xpath('//div[@class="titleHead"]//div[@class="newsDate"]/text()')
    img_url = tree.xpath('//div[@class="main_content"]//img/@data-original')

    if (len(title)>0):
        title = str(title[0]).strip()
    else:
        print("版面格式警报","21财经",url)
        return
    source = str(source[0]).strip() if (len(source)>0) else ""
    sourTime = str(sourTime[0]).strip() if (len(sourTime)>0) else ""
    art = ""
    for it in context_zz.finditer(page_text):
        art = it.group("context")
    art.strip()


    img_list = ""
    img_path = "/home/NRGLXT/source/media/img/"
    # img_path = "D:\pythonProject\Pic\\"
    if not os.path.exists(img_path):  # 创建路径
        os.mkdir(img_path)
    for i in range(0, len(img_url)):
        imgfname = sourTime[0:10] + uid + "_" + str(i) + os.path.splitext(img_url[i])[1]
        urllib.request.urlretrieve(img_url[i], filename=img_path + imgfname)  # 下载图片
        art = art.replace(img_url[i], "http://hzlaiqian.com/media/img/" + imgfname)
        img_list = img_list + "http://hzlaiqian.com/media/img/" + imgfname + ","
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    params = (uid, title, art, source, sourTime, url, f_inputTime, img_list, "21财经")
    input_mysql(params)


def page_index_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        task.add_done_callback(article_get)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


# url = ['https://m.21jingji.com/article/20220413/herald/f5c5828a64b87d7ea198c30f173b55d3.html']
# page_index_get(url)
