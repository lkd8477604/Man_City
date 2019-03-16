#-*- coding:utf-8 -*-
#_author:John
#date:2018/9/10 19:37
#softwave: PyCharm
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re, json
import pymongo
import lxml
class Man_City():
    def __init__(self):
        self.header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        }

    def news_man(self):
        #这是js动态生成的页面，需要找到对应的js网页，再用正则表达式找到所需内容
        man_163_url = 'http://sports.163.com/special/000587PO/newsdata_epl_mch.js?callback=data_callback'
        man_163_data = requests.get(man_163_url, headers=self.header)
        man_163_soup = BeautifulSoup(man_163_data.text, 'lxml').get_text()
        title_re = re.compile('title\":\"(.*?)\",')
        url_re = re.compile('docurl\":\"(.*?)\",')
        tienum_re = re.compile('tienum\":(\d+),')
        pub_date_re = re.compile('time\":\"(.*?)\",')

        titles = title_re.findall(man_163_soup)
        urls = url_re.findall(man_163_soup)
        tienums = tienum_re.findall(man_163_soup)
        pub_dates = pub_date_re.findall(man_163_soup)

        for title, url, tienum, pub_date in zip(titles, urls, tienums, pub_dates):
            data = {
                'title': title,
                'url': url,
                # 'tienum': tienum,
                #将字符串的时间转换成时间模式再传入数据库，以便之后以时间进行排序
                'pub_date': datetime.strftime(datetime.strptime(pub_date, '%m/%d/%Y %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

            }
            print(data)
            self.add_to_mongodb(db_name='163', data=data)

    def sina_man_news(self):
        #跟163一样先找到真正的网页，得到的是一个json格式的页面，转换一下再取内容
        url = 'http://interface.sina.cn/pc_zt_api/pc_zt_press_news_doc.d.json?subjectID=68265&cat=&size=40&page=1&channel=sports&callback=jsonpcallback1536942563301'
        data_get = requests.get(url, headers= self.header)
        #获取的网页内容大括号里面的是json数据，用正则表达式获取大括号里面的内容得到json格式数据
        data_re = re.compile('\((.*?)\)')
        soup_data = data_re.findall(data_get.text)[0]
        soup = json.loads(soup_data)
        for i in soup['result']['data']:
            # 观察发现日期是放在url中的，把日期分离出来
            pub_date_soup = i['url'].split('/')[-2]
            data = {
                'title': i['title'],
                'url': i['url'],
                #转换时间格式
                'pub_date':datetime.strftime(datetime.strptime(pub_date_soup, '%Y-%m-%d'), '%Y-%m-%d')
            }
            print(data)
            self.add_to_mongodb(db_name='sina', data=data)

    def qq_man_news(self):
        #腾讯里面的曼城新闻没有用js生成，是静态的网页，直接用bs4获取
        url='http://sports.qq.com/premierleague/'
        data_get=requests.get(url, headers=self.header)
        soup = BeautifulSoup(data_get.text, 'lxml')
        titels = soup.select('.newsul.newsCont2 .news_txt a')
        for i in titels:
            # 跟新浪一样的，日期包含在url中
            pub_date_soup = i.get('href').split('/')[-2]
            data = {
                'title': i.get_text(),
                'url': 'http://sports.qq.com/'+ i.get('href'),
                #转换时间格式
                'pub_date':datetime.strftime(datetime.strptime(pub_date_soup, '%Y%m%d'), '%Y-%m-%d')
            }
            self.add_to_mongodb(db_name='qq', data=data)
            print(data)

    def add_to_mongodb(self, db_name, data):
        #分别命名存入数据库
        client = pymongo.MongoClient('localhost', 27017)
        Man_City = client['Man_City']
        db_name = Man_City[db_name]
        #用日期倒序排列，取出60个标题放到列表，如果新获取的数据标题不在这60个标题列表中就加入数据库中，避免同一个新闻多次存入数据库
        pipeline= [
            {'$sort':{'pub_date':-1}},
            {'$limit':60,},
        ]
        titel_list = [db['title'] for db in db_name.aggregate(pipeline)]
        if data['title'] not in titel_list:
            db_name.insert_one(data)

    def main(self):
        self.news_man()
        self.sina_man_news()
        self.qq_man_news()
if __name__ == '__main__':
    M = Man_City()
    M.news_man()
    M.sina_man_news()
    M.qq_man_news()
    # M.add_to_mongodb(db_name='sina')
