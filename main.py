"""
A scraper for WeChat offical account articles' titles, views, likes, # of comments, and real urls, and also looking for certain elements (target_html) in html.

POST HTTP request to WeChat API http://mp.weixin.qq.com/mp/getappmsgext to get response.
Requires a file named "wechat.json" to store sensitive information.

JSON file structure: 
{
    "account_profile": ******,

    "appmsg_token": ******,

    "__biz": ******,

    "target_html": ******
}

account_profile is the article history url of WeChat official account. Clicking "View Message History" on PC or Mac WeChat client, then look for a url start with "https://mp.weixin.qq.com/mp/getmasssendmsg?" and followed by a tons of parameters in your MITM proxy.

appmsg_token is the token for getting things like views, likes, # of comments of articles (JSON). It can be found using MITM proxy as well, just clicking an article and look for a url start with "https://mp.weixin.qq.com/mp/getappmsgext?". This token will expire after centain period of time.

__biz is the unique identifier associate with WeChat account. It can be find inside the account_profile url but I am not sure it is always there.

target_html is the html elements that we are looking for in articles. This is useful if one of the desired output is to check which articles have certain ads banner or image or other stuff. The JSON file can not have this one if it is not desired.

"""
import time
import datetime
import json
import html
import csv
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = json.loads(open("wechat.json", mode="r").read())

account_profile = config["account_profile"]
appmsg_token = config["appmsg_token"]

# setting
# customize offset, default 0, 200
start = 0
max = 400


try:
    target_html = config["target_html"]
except:
    target_html = None


class History:
    def __init__(self):
        headers = {
            "User-Agent":
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.14(0x17000e28) NetType/WIFI Language/en",
        }
        self.s = requests.Session()
        self.s.get(account_profile, headers=headers, verify=False)
        self.biz = account_profile.split("&")[0].split("=")[1] + "=="
        self.uin = account_profile.split("&")[1].split("=")[1]
        self.key = account_profile.split("&")[2].split("=")[1]
        self.pass_ticket = account_profile.split("&")[-1].split("=")[1]

        global biz
        biz = self.biz

    def get_articles(self, max, start=0):
        """get articles title and urls from WeChat official account history.

        Args:
            max (int): maximum offset to get. 10 groups of articles for every 10 offset. A WeChat official account can send one group article per day but the amount of article may vary.
            start (int, optional): start offset. Defaults to 0.

        Returns:
            list: [{"title": "******", "url": "******"}, {"title": "******", "url": "******"},...]
        """
        article_list_url = "https://mp.weixin.qq.com/mp/profile_ext"
        article_list = []
        while start <= max:
            params = {
                'action': "getmsg",
                '__biz': self.biz,
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
                main_article = {}  # unique article
                multi_article = {}  # repeated article(s)
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
        """get read, like, comment for an article using API.

        Returns:
            triple: readNum, likeNum, comment_count
        """
        # get mid, idx, sn from url paramaters
        mid = self.url.split("&")[1].split("=")[1]
        idx = self.url.split("&")[2].split("=")[1]
        sn = self.url.split("&")[3].split("=")[1]
        #_biz = self.url.split("&")[0].split("_biz=")[1]

        # API for read, like, comment, etc.
        url = "http://mp.weixin.qq.com/mp/getappmsgext"

        # add Cookie to avoid login requirement，User-Agent is better to be mobile device
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
            "__biz": biz,
            "mid": mid,
            "sn": sn,
            "idx": idx,
            "key": key,
            "pass_ticket": pass_ticket,
            "appmsg_token": appmsg_token,
            "uin": uin,
            "wxtoken": "777",
        }

        content = self.session.post(url, headers=headers, data=data,
                                    params=params, verify=False).json()

        # get read, like, and comment from response
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

        time.sleep(1)
        return readNum, likeNum, comment_count

    def check_content(self):
        """look up for certain element in html.

        Returns:
            int: 1 = exist, 0 = not exist
        """
        exist = 0
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400"
        }
        html = self.session.get(self.url, headers=headers, verify=False).text
        if target_html != None:
            if target_html in html:
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
    # prevent over max error
    while True:
        try:
            a_list = history.get_articles(start=start, max=max)
            break
        except:
            max -= 1
            print(f"maxout at {max}")
    print(a_list)
    for a in a_list:
        print(a)
        print(f"article # {count}")
        # prevent no title and url error
        if a.get('title') == '':
            print('NO TITLE')
        if a.get('url') == '':
            print('NO URL')
            print("=======================")
            continue
        article = Article(a['url'], history.s)
        a['readnum'], a['likenum'], a['comment_count'] = article.get_info()
        a['banner'] = article.check_content()
        print("=======================")
        write_table(a)
        if count % 10 == 0:
            csvfile.flush()
        count += 1

    csvfile.close()
