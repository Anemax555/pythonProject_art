import asyncio
import time
import pymysql
import aiohttp
from lxml import etree
from redis import StrictRedis
from hashlib import md5

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'}

def input_redis(url_id):
    redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis.sismember('operationlist', url_id):
        return True
    else:
        redis.sadd('operationlist', url_id)
        return False

def input_mysql(params):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_operation (f_id,f_local,f_url,f_title,f_type,f_source,f_inputTime) values (%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


async def get_requests(url):
    async with aiohttp.ClientSession() as sess:
        async with await sess.get(url=url, headers=headers) as resp:
            page_text = await resp.text()
            if (resp.status != 200):
                print("Erro:  ", resp.status, url)
            return page_text


def news_list_get(t):
    page_text = t.result()
    tree = etree.HTML(page_text)
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())

    top_list = tree.xpath("//div[@class='fr tt_word yah']/div[@class='item_txt']")
    for i in range(len(top_list)):
        top_url = top_list[i].xpath('./p/a/@href')
        top_title = top_list[i].xpath('./p/a/text()')
        news_type = "头条"
        for j in range(len(top_url)):
            news_local = news_type + str(i + 1) + "-" + str(j + 1)
            secret = md5()
            secret.update(top_url[i].encode())
            news_id = "ths-top" + secret.hexdigest()
            if not input_redis(news_id):
                params = (news_id, news_local, top_url[j], top_title[j], news_type, "同花顺",f_inputTime)
                input_mysql(params)
    yw_list = tree.xpath('//div[@data-taid="web_ywsl"]/ul')
    for i in range(len(yw_list)):
        yw_url = yw_list[i].xpath('./li/a/@href')
        yw_title = yw_list[i].xpath('./li/a/text()')
        news_type = "要闻"
        for j in range(len(yw_url)):
            if (str(yw_url[j]).find("http:") == -1):
                news_url = "http:" + str(yw_url[j])
            else:
                news_url = str(yw_url[j])
            news_title = str(yw_title[j])
            news_local = news_type + str(i + 1) + "-" + str(j + 1)
            secret = md5()
            secret.update(yw_url[j].encode())
            news_id = "ths-yw" + secret.hexdigest()
            if not input_redis(news_id):
                params = (news_id, news_local, news_url, news_title, news_type, "同花顺",f_inputTime)
                input_mysql(params)


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
        'https://www.10jqka.com.cn/'
    ]
    page_index_get(urls_index)