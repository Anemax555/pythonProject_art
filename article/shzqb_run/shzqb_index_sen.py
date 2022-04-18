import time

import requests

f_time = round(time.time() * 1000)
url = f'https://app.cnstock.com/api/waterfall?callback=jQuery191038350279236238904_1656674717711&colunm=qmt-scp_gsxw&page=3&num=10&showstock=0&_{f_time}'
heards = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

cookie = 'temp_uid=tp_16466398509670; Hm_lvt_5f1ddd842219521824ad49f82d8a712c=1646789734,1646793453,1646895344,1646896977; SL_G_WPT_TO=zh; SL_wptGlobTipTmp=1; SL_GWPT_Show_Hide_tmp=1'
cookie_dict = {i.split("=")[0]: i.split("=")[-1] for i in cookie.split("; ")}
print(cookie_dict)
resp = requests.get(url, headers=heards, cookies=cookie_dict)
print(resp.text)

def get_urls(max_page):
    start_url = 'http://news.cnstock.com/news/sns_yw/'
    urls = []
    for i in range(1,max_page+1):
        spec_url = start_url + str(i) if i>1 else start_url + 'index.html'
        source = pq(spec_url)
        urls += [item.attr('href') for item in source('.new-list li a').items()]
    return urls