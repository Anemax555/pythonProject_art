import asyncio
import aiohttp
import shzqb_art
import time
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
    url = page["url"]
    tree = etree.HTML(page_text)
    news = tree.xpath("//ul[@id='j_waterfall_list']/li/h2/a/@href")
    if (len(news) == 0):
        news = tree.xpath(
            "//ul[@class='news-des-list'][1]/li/p[@class='tit']/a/@href")
    if (len(news) == 0):
        news = tree.xpath(
            "//div[@class='box ind-tab-more']/div[@id='focus-show']/ul[@class='focus-list'][1]/li/h2/a/@href")

    if len(news) == 0:
        print("Erro", url)
    secret = md5()
    for new in news:
        secret.update(new.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            new_info = {"furl": url, "url": new}
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
    # urls_index = ['https://stock.cnstock.com/xg/sx_xgjj']

    f = open('/home/NRGLXT/pythonproject/project_art/py_projiec_358/article/shzqb_run/shzqb', mode='r')
    url = f.readline()
    urls_index = []
    while url:
        urls_index.append(url.strip())
        url = f.readline()
    f.close()

    # print(len(urls_index), urls_index)
    # print(urls_index)

    page_index_get(urls_index)

    n = 0
    news_url = []
    for i in range(len(news_list)):
        if (n == 10):
            shzqb_art.page_news_get(news_url)
            news_url = []
            n = 0
            time.sleep(1)
        else:
            n = n + 10
            news_url.append(news_list[i])
    if n != 0:
        shzqb_art.page_news_get(news_url)

    print("shzqb更新 ", len(news_list), "条数据")

    news_list.clear()