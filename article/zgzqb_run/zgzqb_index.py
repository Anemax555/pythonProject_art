import asyncio
import time
import aiohttp
import zgzqb_art
from tqdm import tqdm
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
            page = {"url": url, "page": page_text}
            return page


def get_news(tree):
    news = tree.xpath(
        "//div[@class='box_l1 space_r1']/div[@class='ch_l space_b3']/ul[@class='ch_type3_list']/li/a/@href")


def news_list_get(t):
    page = t.result()
    page_text = page["page"]
    url = page["url"]
    tree = etree.HTML(page_text)
    # ===============================================头条中间板块
    news = tree.xpath("//ul[@class='ch_type3_list some-list']/li[@class='item']/a/@href")

    if len(news) >= 45:
        news = news[:19]
    if len(news) == 0:
        news = tree.xpath(
            "//div[@class='box_l1 space_r1']/div[@class='ch_l space_b3']/ul[@class='ch_type3_list']/li/a/@href")
    if (len(news) == 0):
        news = tree.xpath("//div[@class='box_ch']/div[@class='box_l1 space_r1']/ul[@class='ch_type3_list']/li/a/@href")
    if (url == 'https://toujiao.cs.com.cn/'):
        news = tree.xpath("//div[@class='box1200 list_col2 space_b2']/div[@class='ch_index_s']/ul/li/a/@href")
    if (len(news) == 0):
        print("Erro", url)
    secret = md5()
    for new in news:
        secret.update(new.encode())
        newid = secret.hexdigest()
        if not input_redis(newid):
            new_1 = str(new).split('/')
            new_2 = '/'.join(new_1[1:])
            new_3 = str(url).strip('/')
            if ('http' in new):
                news_list.append(new)
            else:
                if (new_1[0] == '..'):
                    new_4 = new_3.replace(new_3.split('/')[-1], '') + new_2
                    new_info = {"furl": url, "url": new_4}
                    news_list.append(new_info)
                else:
                    new_4 = new_3 + '/' + new_2
                    new_info = {"furl": url, "url": new_4}
                    news_list.append(new_info)

            # if (".." in new):
            #     news_list.append("https://www.cs.com.cn/" + str(new).strip('../'))
            # else:
            #     news_list.append(str(url) + str(new).strip('.'))


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
    f = open('/home/NRGLXT/pythonproject/project_art/py_projiec_358/article/zgzqb_run/zgzqb', mode='r')
    url = f.readline()
    urls_index = []
    while url:
        urls_index.append(url.strip())
        url = f.readline()
    f.close()
    page_index_get(urls_index)

    n = 0
    news_url = []
    for i in range(len(news_list)):
        if (n == 10):
            zgzqb_art.page_news_get(news_url)
            news_url = []
            n = 0
            time.sleep(1)
        else:
            n = n + 1
            news_url.append(news_list[i])
    if n != 0:
        zgzqb_art.page_news_get(news_url)
    print("中国证券报index：更新 ", len(news_list), "条数据")
    news_list.clear()

# main()
