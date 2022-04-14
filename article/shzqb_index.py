import asyncio
import aiohttp
import shzqb_art
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
            return page_text


def news_list_get(t):
    page_text = t.result()
    tree = etree.HTML(page_text)
    news = tree.xpath("//ul[@id='j_waterfall_list']/li/h2/a/@href")
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
    urls_index = [
        'https://news.cnstock.com/news/sns_yw/index.html',
        'https://news.cnstock.com/news/sns_jg/index.html',
        'https://news.cnstock.com/industry',
        'https://company.cnstock.com/company/scp_gsxw',
        'https://ggjd.cnstock.com/company/scp_ggjd/tjd_ggkx',
        'https://ggjd.cnstock.com/company/scp_ggjd/tjd_bbdj',
        'https://jrz.cnstock.com/',
        'https://www.cnstock.com/'
    ]
    page_index_get(urls_index)
    if (len(news_list)>0):
        shzqb_art.page_news_get(news_list)
    print("更新 ",len(news_list),"条数据")