import asyncio
import re
import pymysql
import aiohttp
import time
from lxml import etree
from redis import StrictRedis
from hashlib import md5


def input_mysql(params):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_operation (f_id,f_local,f_url,f_title,f_type,f_source,f_inputTime) values (%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(sql, params)
    con.commit()
    con.close()


def input_redis(url_id):
    redis = StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    if redis.sismember('operationlist', url_id):
        return False
    else:
        # redis.sadd('operationlist', url_id)
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
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    num = 0

    # ================================================头条暂时不要
    # top_title = tree.xpath("//div[@class='focuspic']//a/img/@alt")
    # top_url = tree.xpath("//div[@class='focuspic']//a/@href")
    # for i in range(len(top_url)):
    #     news_local = "头条-" + str(i + 1)
    #     news_type = "头条"
    #     secret = md5()
    #     secret.update(top_url[i].encode())
    #     news_id = "sina-top" + secret.hexdigest()
    #     if not input_redis(news_id):
    #         params = (news_id, news_local, top_url[i], top_title[i], news_type, "新浪财经", f_inputTime)
    #         input_mysql(params)
    #         num = num + 1

    news_title_fst = tree.xpath("//div[@id='blk_hdline_01']/h3/a/text()")
    news_url_fst = tree.xpath("//div[@id='blk_hdline_01']/h3/a/@href")
    news_zw = tree.xpath("//div[@id='blk_hdline_01']/h3")
    for i in range(len(news_zw)):
        news_type = "热点"
        zw_title = news_zw[i].xpath('./a/text()')
        zw_url = news_zw[i].xpath('./a/@href')
        for j in range(len(zw_title)):
            news_local = news_type + str(i + 1)
            secret = md5()
            secret.update(zw_url[j].encode())
            news_id = "sina-yw" + secret.hexdigest()
            if not input_redis(news_id):
                params = (news_id, news_local, zw_url[j], zw_title[j], news_type, "新浪财经", f_inputTime)
                input_mysql(params)
                # print(params)
                num = num + 1
    art = tree.xpath("//div[@id='blk_hdline_01']")
    art_zz = re.compile(r'<div class="m-hdline" id="blk_hdline_01".*?</div>', re.S)
    news_list_zz = re.compile(r'</h3>.*?<h3 data-client="headline">', re.S)

    lastnews_list = art[0].xpath('./h3[last()]/following-sibling::p')

    # print(etree.tostring(lastnews_list[1],encoding='utf-8',pretty_print=True,method='html').decode())
    n = 1
    for it in art_zz.finditer(page_text):
        for news_list in news_list_zz.finditer(it.group()):
            tree = etree.HTML(news_list.group())
            news_p = tree.xpath('//p')
            for i in range(len(news_p)):
                news_title = news_p[i].xpath('./a/text()')
                news_url = news_p[i].xpath('./a/@href')
                news_type = "热点"
                for j in range(len(news_title)):
                    news_local = news_type + str(n)
                    secret = md5()
                    secret.update(news_url[j].encode())
                    news_id = "sina-yw" + secret.hexdigest()
                    if not input_redis(news_id):
                        params = (news_id, news_local, news_url[j], news_title[j], news_type, "新浪财经", f_inputTime)
                        # input_mysql(params)
                        # print(params)
                        num = num + 1
            n = n + 1
    for i in range(len(lastnews_list) - 1):
        news_url = lastnews_list[i].xpath('./a/@href')
        news_title = lastnews_list[i].xpath('./a/text()')

        for j in range(len(news_title)):
            if ("html" in news_url[j]):
                news_local = news_type + str(n)
                secret = md5()
                secret.update(news_url[j].encode())
                news_id = "sina-yw" + secret.hexdigest()
                if not input_redis(news_id):
                    params = (news_id, news_local, news_url[j], news_title[j], news_type, "新浪财经", f_inputTime)
                    input_mysql(params)
                    # print(params)
                    num = num + 1
    print("新浪更新", num, "条数据")


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
        'https://finance.sina.com.cn/'
    ]
    page_index_get(urls_index)
