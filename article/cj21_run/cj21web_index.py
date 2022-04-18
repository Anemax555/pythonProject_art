import asyncio
import time
import cj21web_art
import aiohttp
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
                print("Erro:  ", resp.status, url)
            return page_text


def news_list_get(t):
    page_text = t.result()
    tree = etree.HTML(page_text)
    news = tree.xpath("/html/body/div[@class='layout']/div[@class='col-l']/div[@class='news']/a/@href")
    secret = md5()
    for new in news:
        secret.update(new.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            news_list.append(new)


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
    f = open('/home/NRGLXT/pythonproject/project_art/py_projiec_358/article/cj21_run/21cj_web', mode='r')
    url = f.readline()
    urls_index = []
    while url:
        urls_index.append(url.strip())
        url = f.readline()
    f.close()
    # print(len(urls_index),urls_index)
    page_index_get(urls_index)
    # print(news_list)
    n = 0
    news_url = []
    for i in range(len(news_list)):
        if (n == 10):
            cj21web_art.page_index_get(news_url)
            news_url = []
            n = 0
            time.sleep(1)
        else:
            n = n + 1
            news_url.append(news_list[i])
    if n != 0:
        cj21web_art.page_index_get(news_url)
    print("21JJ Web_index更新 ", len(news_list), "条数据")
    news_list.clear()

# main()
