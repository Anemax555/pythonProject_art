import asyncio
import aiohttp
import pymysql
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
        return True
    else:
        redis.sadd('operationlist', url_id)
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

    top_url = tree.xpath("//div[@class='nmlist']/h1//a/@href")
    topsnd_url = tree.xpath("//div[@class='nmlist']/ul[1]//a/@href")
    top_title = tree.xpath("//div[@class='nmlist']/h1//a/text()")
    topsnd_title = tree.xpath("//div[@class='nmlist']/ul[1]//a/text()")
    for i in range(len(top_url)):
        news_type = "焦点"
        news_local = "焦点"
        secret = md5()
        secret.update(top_url[i].encode())
        news_id = "eastmoney-top" + secret.hexdigest()
        if not input_redis(news_id):
            params = (news_id, news_local, top_url[i], top_title[i], news_type, "东方财富", f_inputTime)
            input_mysql(params)
            num = num + 1
    for i in range(len(topsnd_url)):
        news_type = "焦点"
        news_local = "焦点"
        secret = md5()
        secret.update(topsnd_url[i].encode())
        news_id = "eastmoney-top" + secret.hexdigest()
        if not input_redis(news_id):
            params = (news_id, news_local, topsnd_url[i], topsnd_title[i], news_type, "东方财富", f_inputTime)
            input_mysql(params)
            num = num + 1
    yw_ul = tree.xpath('//div[@tracker-eventcode="dfcfwsy_sp_cjdd12_bgl"]/ul')
    for i in range(len(yw_ul)):
        yw_zw = yw_ul[i].xpath('./li[1]')
        for k in range(len(yw_zw)):
            yw_Btitle = yw_zw[k].xpath('./a/strong/text()')
            yw_Burl = yw_zw[k].xpath('./a/@href')
            for j in range(len(yw_Btitle)):
                if (yw_Btitle[j] == '评' or yw_Btitle[j] == '热议'):
                    continue
                news_type = "热点"
                news_local = "热点" + str(i + 1)
                secret = md5()
                secret.update(yw_Burl[j].encode())
                news_id = "eastmoney-yw" + secret.hexdigest()
                if not input_redis(news_id):
                    params = (news_id, news_local, yw_Burl[j], yw_Btitle[j], news_type, "东方财富", f_inputTime)
                    input_mysql(params)
                    num = num + 1
        yw_fw = yw_ul[i].xpath('./li')
        if i > 0:
            yw_fw = yw_fw[1:]
        for k in range(len(yw_fw)):
            yw_title = yw_fw[k].xpath('./a/text()')
            yw_url = yw_fw[k].xpath('./a/@href')
            for j in range(len(yw_url)):
                news_local = "热点" + str(i + 1)
                secret = md5()
                secret.update(yw_url[j].encode())
                news_id = "eastmoney-yw" + secret.hexdigest()
                if not input_redis(news_id):
                    params = (news_id, news_local, yw_url[j], yw_title[j], news_type, "东方财富", f_inputTime)
                    input_mysql(params)
                    num = num + 1
    yw2_ul = tree.xpath('//div[@tracker-eventcode="dfcfwsy_sp_cjdd34_bgl"]/ul')
    for i in range(len(yw2_ul)):
        yw_zw = yw2_ul[i].xpath('./li[1]')
        for k in range(len(yw_zw)):
            yw_Btitle = yw_zw[k].xpath('./a/strong/text()')
            yw_Burl = yw_zw[k].xpath('./a/@href')
            for j in range(len(yw_Btitle)):
                if yw_Btitle[j] == '评':
                    continue
                news_type = "热点"
                news_local = "热点" + str(len(yw_ul) + i + 1)
                secret = md5()
                secret.update(yw_Burl[0].encode())
                news_id = "eastmoney-yw" + secret.hexdigest()
                if not input_redis(news_id):
                    params = (news_id, news_local, yw_Burl[j], yw_Btitle[j], news_type, "东方财富", f_inputTime)
                    input_mysql(params)
                    num = num + 1
        yw_fw = yw2_ul[i].xpath('./li')[1:]
        for k in range(len(yw_fw)):
            yw_title = yw_fw[k].xpath('./a/text()')
            yw_url = yw_fw[k].xpath('./a/@href')
            for j in range(len(yw_url)):
                news_local = "热点" + str(len(yw_ul) + i + 1)
                secret = md5()
                secret.update(yw_url[j].encode())
                news_id = "eastmoney-yw" + secret.hexdigest()
                if not input_redis(news_id):
                    params = (news_id, news_local, yw_url[j], yw_title[j], news_type, "东方财富", f_inputTime)
                    input_mysql(params)
                    num = num + 1
    print("东财更新", num, "条数据")


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
        'https://www.eastmoney.com/'
    ]
    page_index_get(urls_index)
