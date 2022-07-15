import asyncio
import time
import aiohttp
import zqsb_art
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
    url = page["url"]

    page_home = page["page"]
    hotnews_page_zz = re.compile(r'<div class="hotNews">.*?<div class="maj_right">', re.S)
    hotnews1_page_zz = re.compile(r'<!--财经要闻开始-->.*?<!--财经要闻结束-->', re.S)
    news_list_zz = re.compile(r'<a href="\./(?P<news_url>.*?)" ', re.S)
    hotnews_page = hotnews_page_zz.finditer(page_home)
    hotnews1_page = hotnews1_page_zz.finditer(page_home)
    news_list = []
    for it in hotnews_page:
        hotnews_list = news_list_zz.finditer(it.group())
        for it1 in hotnews_list:
            if it1.group("news_url") != "lh/":
                news_list.append(url + it1.group("news_url"))
    for it in hotnews1_page:
        hotnews1_list = news_list_zz.finditer(it.group())
        for it1 in hotnews1_list:
            news_list.append(url + it1.group("news_url"))
    secret = md5()
    for new in news_list:
        secret.update(new.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            new_info = {"furl": url, "url": new}
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
    urls = ['http://www.stcn.com/']
    page_index_get(urls)

    n = 0
    news_url = []
    for i in range(len(news_list_url)):
        if (n == 10):
            zqsb_art.page_index_get(news_url)
            news_url = []
            n = 0
            time.sleep(1)
        else:
            n = n + 1
            news_url.append(news_list_url[i])
    if n != 0:
        zqsb_art.page_index_get(news_url)

    print("证券时报home：更新 ", len(news_list_url), "条数据")
    news_list_url.clear()
