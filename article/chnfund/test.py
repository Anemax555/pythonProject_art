import json
import requests
import time
import asyncio
import os.path
import pymysql
import urllib.request
import pandas as pd
import aiohttp
from datetime import datetime
from threading import Timer
from hashlib import md5
from redis import StrictRedis
from lxml import etree

url_list = []
title_list = []
sourceTime_list = []

def get_data_news(data):
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    f_id = data["id"]
    f_title = data["title"]
    f_content = data["content"]
    f_source = data["source"]
    f_sourceTime = data["pubDate"]
    f_url = data["url"]

    select_time = "2022-06-30 00:00:00"
    formatted_date1 = datetime.strptime(f_sourceTime,"%Y-%m-%d %H:%M:%S")
    formatted_date2 = datetime.strptime("2022-06-30 00:00:00", "%Y-%m-%d %H:%M:%S")
    formatted_date3 = datetime.strptime("2022-07-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    if (formatted_date1>formatted_date2) and (formatted_date1<formatted_date3):
        params = (f_id, f_title, f_source, f_sourceTime, f_url, f_inputTime, "中国基金报")
        url_list.append(f_url)
        title_list.append(f_title)
        sourceTime_list.append(f_sourceTime)



def get_data_news_list(url):
    resp = requests.get(url)
    data_json = json.loads(resp.text)

    num = 0

    for i in range(len(data_json)):
        f_id = data_json[i]["id"]
        get_data_news(data_json[i])

    data_list = {"url":url_list,"title":title_list,"Date":sourceTime_list}
    data_frame = pd.DataFrame(data_list)
    data_frame.to_excel('chnfund.xls')
    print(data_frame)

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
    print(page_text)



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
    resp = requests.get('https://www.cs.com.cn/../sylm/jsbd/202206/t20220613_6276616.html')
    print(resp)
    url = ['https://www.cs.com.cn/sylm/jsbd/202206/t20220613_6276616.html']
    page_index_get(url)



main()

