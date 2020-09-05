# WeChat Article Scraper

A scraper for scraping WeChat Official Account (公众号) articles' titles, views, likes, # of comments, and real urls, and also looking for certain elements in html.
Article content is not included in the output, but the script is easy to be modifed to do so.

## Before using
Requires a file named "wechat.json" to store sensitive information that can be potentially used for tracking your WeChat ID.

Requires a MITM proxy to get the info from WeChat Mac/PC client.

JSON file structure: 
```
{
    "article_history": ******,

    "appmsg_token": ******,

    "__biz": ******,

    "target_html": ******
}
```

## How to use
1. Make sure your MITM proxy is running and capture HTTPS requests.
2. Open the WeChat Official Account (公众号) you want to scrape, click the button on the upper right side corner, then click 'View Message History" from the dropdown menu.
3. look for a url start with "https://mp.weixin.qq.com/mp/getmasssendmsg?" and followed by a tons of parameters in your MITM proxy. This is the ```article_history```.
4. Open whatever article from the Message History page, then look for a url start with "https://mp.weixin.qq.com/mp/getappmsgext?". From headers of this request, you can get ```appmsg_token``` and ```__biz```.
5. If you want to search for certain html elements such as ads banner or image or text or other stuff, get the html as ```target_html```.
6. Put all of those into the ```wechat.json``` file and run the ```main.py```.