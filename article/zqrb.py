import re
import time
import requests
import pymysql
import os.path
import urllib.request
from concurrent.futures import ThreadPoolExecutor

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}

def download_one_page(url):
    con = pymysql.Connect(host='47.96.18.55', user='crawler', password='123456', database='cnstock_db', port=3306)
    cur = con.cursor()
    sql = 'insert ignore into f_article (f_uid,f_title,f_context,f_source,f_sourceTime,f_sourceAddress,f_inputTime,f_media,f_sourceSite) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    resp = requests.get(url,headers=headers)
    resp.encoding = resp.apparent_encoding
    page_home = resp.text

    news_content_zz = re.compile(r'<div class="news_content">.*?<h1>(?P<title>.*?)</h1>.*?<div class="info_news">(?P<sourceTime>.*?)来源：(?P<source>.*?)</div>.*?<!--con-->(?P<context>.*?)<!--end-->',re.S)
    news_id_zz = re.compile(r'encodeURIComponent.*?title_id=(?P<news_id>.*?)&title.*?</html>',re.S)
    img_url_zz = re.compile(r'<img src="(?P<imgurl>.*?)"',re.S)


    for i in news_id_zz.finditer(page_home):
        news_id = i.group("news_id")

    news_content = news_content_zz.finditer(page_home)
    for it in news_content:
        f_title = re.sub('<[^<]+?>','',it.group("title")).strip()
        f_context = it.group("context").strip()
        f_source = re.sub('<[^<]+?>','',it.group("source")).strip()
        f_sourceTime = re.sub('<[^<]+?>','',it.group("sourceTime")).strip()
        f_sourceAddress = url
        f_inputTime =  time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime())
        imgurls = img_url_zz.findall(it.group())
        imgurls_list = ""
        if (len(imgurls) > 0):
            for i in range(0, len(imgurls)):
                if (imgurls[i].find("http") != -1):
                    imgfname = f_sourceTime[0:10] + news_id + "_" + str(i) + os.path.splitext(imgurls[i])[1]
                    img_path = "/home/NRGLXT/source/media/img/"
                    if not os.path.exists(img_path):
                        os.mkdir(img_path)
                    urllib.request.urlretrieve(imgurls[i], filename=img_path + imgfname)
                    f_context = f_context.replace(imgurls[i], "http://hzlaiqian.com/media/img/" + imgfname)
                    imgurls_list= imgurls_list + "http://hzlaiqian.com/media/img/" + imgfname + ','

        params = (news_id, f_title, f_context, f_source, f_sourceTime, f_sourceAddress, f_inputTime, imgurls_list,"证券日报")
        print(params)

        cur.execute(sql, params)
        con.commit()
        con.close()

def download_main():
    pagm_time=time.time()
    url = "http://www.zqrb.cn/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
    resp = requests.get(url,headers=headers)
    resp.encoding = resp.apparent_encoding
    page_home = resp.text
    news_list=[]

    news_jrjj_zz = re.compile(r'class="content-text2".*?</div>.*?</div>',re.S)
    news_dyzc1_zz = re.compile(r'<div class="first-left1">.*?<div class="tutext">(?P<first_left1>.*?)<!--第一左侧栏1结束-->',re.S)
    news_dyzc2_zz = re.compile(r'<!--第一左侧栏2开始-->.*?<div class="tutext">(?P<first_left2>.*?)<!--第一左侧栏2结束-->',re.S)
    news_cjyw_zz = re.compile(r'<div class="third-left1">.*?<!--第三左侧栏结束-->',re.S)
    #财经要闻版面
    news_gscy_zz = re.compile(r'<div class="jgbt1">.*?<div class="third-left1">(?P<third_left1>.*?)<div class="third-left3">.*?<!--第三右侧栏开始-->',re.S)
    #公司产业版面
    news_jrjg_zz =re.compile(r'<div class="jgbt2">.*?<div class="third-left1">(?P<first_left1>.*?)<div class="third-txt4">(?P<third_txt4>.*?)<!--第四栏结束-->',re.S)
    #金融机构版面
    news_sctz_zz =re.compile(r'div class="jgbt4">.*?<div class="third-left1">(?P<first_left1>.*?)<div class="third-txt4">(?P<third_txt4>.*?)<!--最后右栏开始-->',re.S)
    #市场投资版面
    news_bkzq_zz =re.compile(r'<div class="jgbt3">.*?<div class="third-left5">(?P<tthird_left5>.*?)<!--最后栏结束-->',re.S)
    news_list_zz = re.compile(r'href="(?P<news_url>.*?)"', re.S)

    news_jrjj = news_jrjj_zz.finditer(page_home)

    for it in news_jrjj:
        jrjj_url = news_list_zz.finditer(it.group())
        for it1 in jrjj_url:
            news_list.append(it1.group("news_url"))
    #今日聚焦

    news_dyzc1 = news_dyzc1_zz.finditer(page_home)
    for it in news_dyzc1:
        dyzc1_url = news_list_zz.finditer(it.group("first_left1"))
        for it1 in dyzc1_url:
            news_list.append(it1.group("news_url"))
    #第一左侧边栏1

    news_dyzc2 = news_dyzc2_zz.finditer(page_home)
    for it in news_dyzc2:
        dyzc2_url = news_list_zz.finditer(it.group("first_left2"))
        for it1 in dyzc2_url:
            news_list.append(it1.group("news_url"))
    #第一左侧边栏2

    news_cjyw = news_cjyw_zz.finditer(page_home)
    for it in news_cjyw:
        cjyw_url = news_list_zz.finditer(it.group())
        for it1 in cjyw_url:
            news_list.append(it1.group("news_url"))
    #财经要闻

    news_gscy = news_gscy_zz.finditer(page_home)
    gscy_url_zz = re.compile(r'<p class="text-top5">.*?</p>',re.S)
    for it in news_gscy:
        gscy_url = news_list_zz.finditer(it.group("third_left1"))
        gscy1_url = gscy_url_zz.finditer(it.group())
        for it1 in gscy_url:
            news_list.append(it1.group("news_url"))
        for it1 in gscy1_url:
            result = news_list_zz.finditer(it1.group())
            for it2 in result:
                news_list.append(it2.group("news_url"))
    #公司产业

    news_jrjg = news_jrjg_zz.finditer(page_home)
    for it in news_jrjg:
        jrjg_url = news_list_zz.finditer(it.group("first_left1"))
        for it1 in jrjg_url:
            news_list.append(it1.group("news_url"))
        for it1 in gscy_url_zz.finditer(it.group("third_txt4")):
            jrjg_url = news_list_zz.finditer(it1.group())
            for it2 in jrjg_url:
                news_list.append(it2.group("news_url"))
    #金融机构

    news_sctz = news_sctz_zz.finditer(page_home)
    for it in news_sctz:
        sctz_url = news_list_zz.finditer(it.group("first_left1"))
        for it1 in sctz_url:
            news_list.append(it1.group("news_url"))
        for it1 in gscy_url_zz.finditer(it.group("third_txt4")):
            sctz_url = news_list_zz.finditer(it1.group())
            for it2 in sctz_url:
                news_list.append(it2.group("news_url"))
    #市场投资

    # news_bkzq = news_bkzq_zz.finditer(page_home)
    # for it in news_bkzq:
    #     bkzq_url = news_list_zz.finditer(it.group("tthird_left5"))
    #     for it1 in bkzq_url:
    #         news_list.append(it1.group("news_url"))

    with ThreadPoolExecutor(50) as t:
        for it in news_list:
            if "/index" not in it:
                #download_one_page(it)
                t.submit(download_one_page,it)
    print("zqrb",time.time()-pagm_time)