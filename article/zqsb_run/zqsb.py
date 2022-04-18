import os.path
import re
import time
import urllib.request
import requests
import pymysql
from concurrent.futures import ThreadPoolExecutor

def download_one_page(url):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
    respone = requests.get(url,headers=headers)
    page_home = respone.text

    tit_zz = re.compile(r'<div class="intal_tit">.*?<h2>(?P<title>.*?)</h2>.*?<div class="info">(?P<sourceTime>.*?)<span>来源：(?P<source>.*?)</span>',re.S)
    content_zz = re.compile(r' <div class="txt_con" id="ctrlfscont">(?P<context>.*?)<script type="text/javascript">',re.S)
    img_url_zz = re.compile(r'<img src="(?P<imgurl>.*?)"',re.S)
    news_id_zz = re.compile(r'<div id="NewsArticleID.*?>(?P<news_id>.*?)</div>',re.S)
    for i in news_id_zz.finditer(page_home):
        news_id = i.group("news_id")
    tit = tit_zz.finditer(page_home)
    content = content_zz.finditer(page_home)

    for it in tit:
        f_title=re.sub('<[^<]+?>','',it.group("title")).strip()
        f_sourceTime = re.sub('<[^<]+?>','',it.group("sourceTime")).strip()
        f_source = re.sub('<[^<]+?>','',it.group("source")).strip()

    img_path = "/home/NRGLXT/source/media/img/"
    img_list =[]
    img_path_list = []
    img_url_list = []



    for it in content:
        f_context = it.group("context").strip()
        n=0
        str1 = ""
        for img in img_url_zz.finditer(it.group()):
            imgurl = img.group("imgurl")
            if (imgurl.find("http")== -1):
                imgurl = url.replace(url.split('/')[-1], imgurl.strip('.'))
            if not os.path.exists(img_path):
                os.mkdir(img_path)
            imgname = f_sourceTime[0:10] + news_id+ "_"+ str(n) + os.path.splitext(imgurl)[1]
            filename = img_path+imgname
            urllib.request.urlretrieve(imgurl,filename=filename)
            f_context = f_context.replace(img.group("imgurl"),"http://hzlaiqian.com/media/img/"+imgname)
            str1 = str1 + "http://hzlaiqian.com/media/img/"+imgname + ','
            img_url_list.append(str1)
            img_path_list.append(filename)
            img_list.append(imgname)
            n = n+1
    f_inputTime = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    params = (news_id,f_title,f_context,f_source,f_sourceTime,url,f_inputTime,str1,"证券时报")
    cur.execute(sql, params)
    con.commit()
    con.close()


def download_main():
    url = "http://www.stcn.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
    resp = requests.get(url,headers=headers)
    page_home = resp.text
    hotnews_page_zz = re.compile(r'<div class="hotNews">.*?<div class="maj_right">',re.S)
    hotnews1_page_zz = re.compile(r'<!--财经要闻开始-->.*?<!--财经要闻结束-->',re.S)
    news_list_zz = re.compile(r'<a href="\./(?P<news_url>.*?)" ',re.S)
    hotnews_page = hotnews_page_zz.finditer(page_home)
    hotnews1_page = hotnews1_page_zz.finditer(page_home)
    news_list = []
    for it in hotnews_page:
        hotnews_list = news_list_zz.finditer(it.group())
        for it1 in hotnews_list:
            if it1.group("news_url") !="lh/" :
                news_list.append(url+it1.group("news_url"))
    for it in hotnews1_page:
        hotnews1_list = news_list_zz.finditer(it.group())
        for it1 in hotnews1_list:
            news_list.append(url+it1.group("news_url"))

    with ThreadPoolExecutor(10) as t:
        for it in news_list:
            if ((it.find("video") == -1) and (it.find("html") != -1)):
                t.submit(download_one_page,it)
    print("证券时报")