import asyncio
import time

import aiohttp
import mrcj_art
from redis import StrictRedis
from hashlib import md5
from lxml import etree

news_list = []


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
                print("Erro:  ",resp.status,url)
            page = {"url":url,"page":page_text}
            return page


def news_list_get(t):
    page = t.result()
    page_text = page["page"]
    furl = page["url"]
    tree = etree.HTML(page_text)
    news = tree.xpath('//div[@class="g-list-text"]/div[@class="m-list"]/ul/li/a/@href')
    secret = md5()
    for new in news:
        url = "http:" + str(new)
        secret.update(url.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            new_info = {"furl":furl,"url":url}
            news_list.append(new_info)


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
    f = open("/home/NRGLXT/pythonproject/project_art/py_projiec_358/article/mrjc_run/mjwurl.txt", mode='r')
    url = f.readline()
    urls_index = []
    while url:
        urls_index.append(url.strip())
        if len(urls_index)==10:
            page_index_get(urls_index)
            urls_index=[]
            time.sleep(2)
        url = f.readline()
    f.close()
    if len(urls_index)>0:
        page_index_get(urls_index)

    news_url = []
    for i in range(len(news_list)):
        news_url.append(news_list[i])
        if len(news_url)==10:
            # print(news_url)
            mrcj_art.page_index_get(news_url)
            news_url = []
            time.sleep(2)
    if len(news_url)>0:
        # print(news_url)
        mrcj_art.page_index_get(news_url)
    print(f"每日财经更新：{len(news_list)}条数据")
    news_list.clear()