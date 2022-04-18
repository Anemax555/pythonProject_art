import asyncio
import re
import aiohttp
import sys
sys.path.append("/home/NRGLXT/pythonproject/project_art/py_projiec_358/")
from article.fund_cfh import cfh_art_num1
import time
from redis import StrictRedis
from hashlib import md5

news_list = []


def input_redis(url_id):
    redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis.sismember('urllist', url_id):
        return True
    else:
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
    url_zz = re.compile(r'extend.*?CFHQuote.*?<a href=\\"(?P<url>.*?)\\"',re.S)
    for it in url_zz.finditer(page_text):
        url = it.group('url').strip()
        # news_list.append(url)
        secret = md5()
        secret.update(url.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            news_list.append(url)


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


    # cfh_art_num1.page_index_get(news_list)
    f = open('/home/NRGLXT/pythonproject/project_art/py_projiec_358/article/fund_cfh/cfh_index_page', mode='r')
    url = f.readline()
    urls_index = []
    while url:
        uid = url.split('/')[-1].strip()
        pagenum = 1
        pagesize = 10
        url = f'https://i.eastmoney.com/api/guba/userdynamiclistv2?uid={uid}&pagenum={pagenum}&pagesize={pagesize}'
        urls_index.append(url.strip())
        url = f.readline()
    f.close()
    page_index_get(urls_index)
    n = 0
    news_url = []
    for i in range(len(news_list)):
        if (n == 10):
            cfh_art_num1.page_index_get(news_url)
            news_url = []
            n = 0
            time.sleep(1)
        else:
            n = n + 1
            news_url.append(news_list[i])
    if n != 0:
        cfh_art_num1.page_index_get(news_url)
    print("财富号更新 ",len(news_list),"条数据")
    news_list.clear()