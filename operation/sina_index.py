import asyncio
import re

import aiohttp
from hashlib import md5
from lxml import etree


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

    top_title = tree.xpath("//div[@class='focuspic']//a/img/@alt")
    top_url = tree.xpath("//div[@class='focuspic']//a/@href")
    for i in range(len(top_url)):
        news_loca = "top-" + str(i)
        news_type = "头条"
        params = (news_type, top_title, top_url, news_loca, "新浪财经")
        print()

    news_title_fst = tree.xpath("//div[@id='blk_hdline_01']/h3/a/text()")
    news_url_fst = tree.xpath("//div[@id='blk_hdline_01']/h3/a/@href")

    news_title_fst_zz = re.compile(r'<div class="fin_tabs0_c0" id="fin_tabs0_c0">.*?<style type="text/css">')
    news_list_zz = re.compile(r'</h3>.*?<div class="m-p1-mb1-list m-list-container"')

    a = news_title_fst_zz.findall(page_text)
    print(a)

    b = news_list_zz.findall(a)
    print(b)



# for i in range(len(news_url_fst)):
#     if i<len(news_url_fst)
#         news_list =

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


main()
