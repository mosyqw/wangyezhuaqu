# encoding: utf-8
import requests
import re
from urllib.parse import urlparse
import os.path

def go(url):
    # 解析url
    urls = urlparse(url)
    # 创建文件夹
    site_file = 'site'
    if not os.path.exists(site_file):os.mkdir(site_file)
    site_file = site_file + '/' + re.sub('[\/:*?"<>|]','_',(''.join(urls[1:])))
    if not os.path.exists(site_file):os.mkdir(site_file)
    site_file = site_file + '/'
    # path = urls[0] + '://' + urls[1] + urls[2]
    # 抓取网页信息
    rs = requests.get(url)
    rs.encoding = "utf8"
    html = rs.text
    # 头部
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
    }
    # 返回真实地址
    def getRealUrl(url):
        # 判断是否为网络链接
        if url[0:2] == '//':return 'http:' + url
        if url[0:4] == 'http':return url
        path = urls[2].split('/')
        # url = real_path[0:-1] + url
        path = urls[0] + '://' + urls[1] + '/'.join(path[0:-1])
        if not path.endswith('/'):path += '/'
        url = path + url
        return url

    # 获取文件抓取并修改
    paths = []
    def getSrc(text,ty):
        if ty == 'img':
            if text[1] == '':return text[0]
            url = getRealUrl(text[1])
        else:
            if text[2] == '':return text[0]
            url = getRealUrl(text[2])
        print(url)
        # 抓取文件
        res = requests.get(url,headers=headers)
        if ty != 'img':res.encoding = "utf8"
        url = urlparse(url)[2]
        name = os.path.basename(url)
        if name == '':return text[0]
        # 处理无后缀
        if ty != 'img':
            basename = '.'.join(name.split('.')[0:-1])
            if basename == '':basename = name
            if not name.endswith("." + ty):name = basename + "." + ty
        if re.search('[\/:*?"<>|]',name):return text[0]
        path = ty + "/" + name
        if (path not in paths):
            if not os.path.exists(site_file + ty):os.mkdir(site_file + ty)
            paths.append(url)
            # 写入文件
            fp = open(site_file + path,"w+b")
            if ty == 'img':
                fp.write(res.content)
            else:
                fp.write(bytes(res.text, encoding = "utf8")) #写入数据
            fp.close() #关闭文件
        if ty == 'img':
            return text[0].replace(text[1],path)
        else:
            return text[0].replace(text[2],path)

    def getImg(text):
        return getSrc(text,'img')

    def getJS(text):
        return getSrc(text,'js')

    def getCSS(text):
        return getSrc(text,'css')

    html = re.sub("<img.+?src=[\"|'](.*?)[\"|']", getImg, html)
    html = re.sub("url\([\"|']*?(.*?)[\"|']*?\)", getImg, html)
    html = re.sub("<script((?!>).)*?src=[\"|'](.*?)[\"|']", getJS, html)
    html = re.sub("<link((?!>).)*?href=[\"|'](.*?)[\"|']", getCSS, html)
            
    # 添加index.html
    fp = open(site_file + "index.html","w+b") #打开一个文本文件
    fp.write(bytes(html, encoding = "utf8")) #写入数据
    fp.close() #关闭文件

# 读取站点
with open('site.txt',"r",encoding="utf-8") as f:
    for line in f.readlines():
        go(''.join(line.split()))