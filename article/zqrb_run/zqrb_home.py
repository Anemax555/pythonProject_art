import asyncio
import time
import aiohttp
import zqrb_art
import re
from redis import StrictRedis
from hashlib import md5

news_list_url = []


def input_redis(url_id):
    redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis.sismember('urllist', url_id):
        return True
    else:
        redis.sadd('urllist', url_id)
        return False


async def get_requests(url):
    async with aiohttp.ClientSession() as sess:
        async with await sess.get(url=url) as resp:
            page_text = await resp.text()
            if (resp.status != 200):
                print("Erro:  ", resp.status, url)
            page_text = await resp.text()
            page = {"url": url, "page": page_text}
            return page


def news_list_get(t):
    page = t.result()
    page_home = page["page"]
    url = page["url"]
    news_list = []
    news_jrjj_zz = re.compile(r'class="content-text2".*?</div>.*?</div>', re.S)
    news_dyzc1_zz = re.compile(r'<div class="first-left1">.*?<div class="tutext">(?P<first_left1>.*?)<!--第一左侧栏1结束-->',
                               re.S)
    news_dyzc2_zz = re.compile(r'<!--第一左侧栏2开始-->.*?<div class="tutext">(?P<first_left2>.*?)<!--第一左侧栏2结束-->', re.S)
    news_cjyw_zz = re.compile(r'<div class="third-left1">.*?<!--第三左侧栏结束-->', re.S)
    # 财经要闻版面
    news_gscy_zz = re.compile(
        r'<div class="jgbt1">.*?<div class="third-left1">(?P<third_left1>.*?)<div class="third-left3">.*?<!--第三右侧栏开始-->',
        re.S)
    # 公司产业版面
    news_jrjg_zz = re.compile(
        r'<div class="jgbt2">.*?<div class="third-left1">(?P<first_left1>.*?)<div class="third-txt4">(?P<third_txt4>.*?)<!--第四栏结束-->',
        re.S)
    # 金融机构版面
    news_sctz_zz = re.compile(
        r'div class="jgbt4">.*?<div class="third-left1">(?P<first_left1>.*?)<div class="third-txt4">(?P<third_txt4>.*?)<!--最后右栏开始-->',
        re.S)
    # 市场投资版面
    news_bkzq_zz = re.compile(r'<div class="jgbt3">.*?<div class="third-left5">(?P<tthird_left5>.*?)<!--最后栏结束-->', re.S)
    news_list_zz = re.compile(r'href="(?P<news_url>.*?)"', re.S)

    news_jrjj = news_jrjj_zz.finditer(page_home)

    for it in news_jrjj:
        jrjj_url = news_list_zz.finditer(it.group())
        for it1 in jrjj_url:
            news_list.append(it1.group("news_url"))
    # 今日聚焦

    news_dyzc1 = news_dyzc1_zz.finditer(page_home)
    for it in news_dyzc1:
        dyzc1_url = news_list_zz.finditer(it.group("first_left1"))
        for it1 in dyzc1_url:
            news_list.append(it1.group("news_url"))
    # 第一左侧边栏1

    news_dyzc2 = news_dyzc2_zz.finditer(page_home)
    for it in news_dyzc2:
        dyzc2_url = news_list_zz.finditer(it.group("first_left2"))
        for it1 in dyzc2_url:
            news_list.append(it1.group("news_url"))
    # 第一左侧边栏2

    news_cjyw = news_cjyw_zz.finditer(page_home)
    for it in news_cjyw:
        cjyw_url = news_list_zz.finditer(it.group())
        for it1 in cjyw_url:
            news_list.append(it1.group("news_url"))
    # 财经要闻

    news_gscy = news_gscy_zz.finditer(page_home)
    gscy_url_zz = re.compile(r'<p class="text-top5">.*?</p>', re.S)
    for it in news_gscy:
        gscy_url = news_list_zz.finditer(it.group("third_left1"))
        gscy1_url = gscy_url_zz.finditer(it.group())
        for it1 in gscy_url:
            news_list.append(it1.group("news_url"))
        for it1 in gscy1_url:
            result = news_list_zz.finditer(it1.group())
            for it2 in result:
                news_list.append(it2.group("news_url"))
    # 公司产业

    news_jrjg = news_jrjg_zz.finditer(page_home)
    for it in news_jrjg:
        jrjg_url = news_list_zz.finditer(it.group("first_left1"))
        for it1 in jrjg_url:
            news_list.append(it1.group("news_url"))
        for it1 in gscy_url_zz.finditer(it.group("third_txt4")):
            jrjg_url = news_list_zz.finditer(it1.group())
            for it2 in jrjg_url:
                news_list.append(it2.group("news_url"))
    # 金融机构

    news_sctz = news_sctz_zz.finditer(page_home)
    for it in news_sctz:
        sctz_url = news_list_zz.finditer(it.group("first_left1"))
        for it1 in sctz_url:
            news_list.append(it1.group("news_url"))
        for it1 in gscy_url_zz.finditer(it.group("third_txt4")):
            sctz_url = news_list_zz.finditer(it1.group())
            for it2 in sctz_url:
                news_list.append(it2.group("news_url"))
    secret = md5()
    for new in news_list:
        secret.update(new.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            new_info = {"furl":url,"url":new}
            news_list_url.append(new_info)


def page_index_get(urls):
    tasks = []
    for url in urls:
        c = get_requests(url)  # c是特殊函数返回的协程对象
        task = asyncio.ensure_future(c)  # 任务对象
        task.add_done_callback(news_list_get)
        tasks.append(task)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))


def main():
    urls_index = ['http://www.zqrb.cn/']
    page_index_get(urls_index)

    n = 0
    news_url = []
    for i in range(len(news_list_url)):
        if (n == 10):
            zqrb_art.page_index_get(news_url)
            news_url = []
            n = 0
            time.sleep(1)
        else:
            n = n + 1
            news_url.append(news_list_url[i])
    if n != 0:
        zqrb_art.page_index_get(news_url)
    print("证券日报home：更新 ", len(news_list_url), "条数据")
    news_list_url.clear()
