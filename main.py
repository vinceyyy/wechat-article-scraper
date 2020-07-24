import requests
import time
import datetime
import json
import html
import csv
from urllib.parse import unquote
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 抓包获取公众号历史记录真实url
config = json.loads(open("wechat.json", mode="r").read())

history_url = config["history_url"]

appmsg_token = config["appmsg_token"]

target = config["target"]

class History:
    def __init__(self):
        headers = {
            "User-Agent":
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.14(0x17000e28) NetType/WIFI Language/en",
        }
        self.s = requests.Session()
        self.s.get(history_url, headers=headers, verify=False)
        self.uin = unquote(history_url.split("&")[1].split("=")[1])
        self.key = unquote(history_url.split("&")[2].split("=")[1])
        self.pass_ticket = unquote(history_url.split("&")[9].split("=")[1])

    def get_articles(self, max, start=0):
        article_list_url = "https://mp.weixin.qq.com/mp/profile_ext"
        article_list = []
        while start <= max:
            params = {
                'action': "getmsg",
                '__biz': "MzI1MzA0MDkyMg==",
                'f': "json",
                'offset': start,
                'count': 10,
                'is_ok': 1,
                'scene': 124,
                'uin': 777,
                'key': 777,
                'pass_ticket': "",
                'wxtoken': "",
                'appmsg_token': appmsg_token,
                'x5': 0,
                'f': "json"
            }
            response = self.s.get(
                article_list_url, params=params, verify=False).json()

            for a in json.loads((response['general_msg_list']))['list']:
                # print(a)
                main_article = {}
                multi_article = {}
                main_article['title'] = html.unescape(
                    a['app_msg_ext_info']['title'])
                main_article['url'] = a['app_msg_ext_info']['content_url']
                main_article['date'] = datetime.datetime.fromtimestamp(
                    a['comm_msg_info']['datetime']).strftime('%Y-%m-%d %H:%M:%S')
                article_list.append(main_article)
                try:
                    for m in a['app_msg_ext_info']['multi_app_msg_item_list']:
                        multi_article['title'] = html.unescape(
                            m['title'])
                        multi_article['url'] = html.unescape(
                            m['content_url'])
                        multi_article['date'] = main_article['date']
                        article_list.append(multi_article)
                except:
                    pass
            start += 10
        return article_list

class Article:
    def __init__(self, url, session):
        self.url = url
        self.session = session
    
    def get_info(self):
        # 获得mid,_biz,idx,sn 这几个在link中的信息
        mid = self.url.split("&")[1].split("=")[1]
        idx = self.url.split("&")[2].split("=")[1]
        sn = self.url.split("&")[3].split("=")[1]
        _biz = self.url.split("&")[0].split("_biz=")[1]

        # 目标url
        url = "http://mp.weixin.qq.com/mp/getappmsgext"
        # 添加Cookie避免登陆操作，这里的"User-Agent"最好为手机浏览器的标识
        phoneCookie = "wxtokenkey=777; rewardsn=; wxuin=2529518319; devicetype=Windows10; version=62060619; lang=zh_CN; pass_ticket=4KzFV+kaUHM+atRt91i/shNERUQyQ0EOwFbc9/Oe4gv6RiV6/J293IIDnggg1QzC; wap_sid2=CO/FlbYJElxJc2NLcUFINkI4Y1hmbllPWWszdXRjMVl6Z3hrd2FKcTFFOERyWkJZUjVFd3cyS3VmZHBkWGRZVG50d0F3aFZ4NEFEVktZeDEwVHQyN1NrNG80NFZRdWNEQUFBfjC5uYLkBTgNQAE="
        headers = {
            "Cookie":
            phoneCookie,
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400"
        }
        data = {
            "is_only_read": "1",
            "is_temp_url": "0",
            "appmsg_type": "9",
            'reward_uin_count': '0'
        }
        params = {
            "__biz": _biz,
            "mid": mid,
            "sn": sn,
            "idx": idx,
            "key": key,
            "pass_ticket": pass_ticket,
            "appmsg_token": appmsg_token,
            "uin": uin,
            "wxtoken": "777",
        }

        # 使用post方法进行提交
        content = self.session.post(url, headers=headers, data=data,
                                    params=params, verify=False).json()

        # 提取其中的阅读数和点赞数
        #print(content["appmsgstat"]["read_num"], content["appmsgstat"]["like_num"])
        try:
            readNum = content["appmsgstat"]["read_num"]
            print("reads:", readNum)
        except:
            readNum = 0
        try:
            likeNum = content["appmsgstat"]["like_num"]
            print("likes:", likeNum)
        except:
            likeNum = 0
        try:
            comment_count = content["comment_count"]
            print("true:" + str(comment_count))
        except:
            comment_count = -1
            print("false:" + str(comment_count))

        # 歇3s，防止被封
        time.sleep(1)
        return readNum, likeNum, comment_count

    def check_content(self):
        exist = 0
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400"
        }
        html = self.session.get(self.url, headers=headers, verify=False).text
        if target in html:
            exist = 1
        print(f"banner: {exist}")
        return exist


csvfile = open('wechat_article_banner.csv', 'a', newline='')
header = ["title", "url", "date", "readnum", "likenum",
          'comment_count', "banner"]

def write_table(data):
    writer = csv.DictWriter(csvfile, header)
    writer.writerow(data)

if __name__ == '__main__':
    count = 1
    history = History()
    uin = history.uin
    key = history.key
    pass_ticket = history.pass_ticket
    a_list = history.get_articles(200)
    print(a_list)
    for a in a_list:
        print(f"article # {count}")
        article = Article(a['url'], history.s)
        a['readnum'], a['likenum'], a['comment_count'] = article.get_info()
        a['banner'] = article.check_content()
        print(a)
        print("=======================")
        write_table(a)
        count += 1



    csvfile.close()
    
