import base64
import json
import random
import time

import scrapy
from bs4 import BeautifulSoup
from loguru import logger
from redis import Redis

cookies = "_ga=GA1.1.1454877146.1696779290; connect.sid=s%3AC57qJhJ-KlST2qS36vSp_Z1uzCQzXDKb.CJw%2F48gT77yWugbADmvmnQBI060e6xgkFtS%2BSfdmZmI; _ga_N09TEJHT2X=GS1.1.1696859567.3.1.1696859668.0.0.0_ga=GA1.1.1454877146.1696779290; connect.sid=s%3AC57qJhJ-KlST2qS36vSp_Z1uzCQzXDKb.CJw%2F48gT77yWugbADmvmnQBI060e6xgkFtS%2BSfdmZmI; _ga_N09TEJHT2X=GS1.1.1696859567.3.1.1696859668.0.0.0_ga=GA1.1.1454877146.1696779290; connect.sid=s%3AC57qJhJ-KlST2qS36vSp_Z1uzCQzXDKb.CJw%2F48gT77yWugbADmvmnQBI060e6xgkFtS%2BSfdmZmI; _ga_N09TEJHT2X=GS1.1.1696859567.3.1.1696859668.0.0.0"
COOKIES = {i[0].strip(): i[1].strip() for i in cookies.split(";")}
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://52fenhongbao.com",
    "Cookie": cookies,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
}
CATEGORIES = ["楼凤兼职", "高端外围", "黑店曝光", "丝足按摩", "洗浴桑拿", "酒店宾馆", "黑凤曝光", "校园霸凌"]

client = Redis("192.168.3.13", db=1)


class FlFhbSpider(scrapy.Spider):
    name = "fl.fhb"  # 粉红豹

    # 降低效率，单线程，每个请求延迟4秒
    # custom_settings = {"CONCURRENT_REQUESTS": 4, "DOWNLOAD_DELAY": 1}

    def __init__(self, param, **kwargs):
        super().__init__(**kwargs)
        s_param = base64.b64decode(param).decode()
        self.param = json.loads(s_param)
        self.api_id = self.param.get("api_id")
        self.api_hash = self.param.get("api_hash")
        self.session_name = self.param.get("session_name")
        proxy = self.param.get("proxy")
        self.clash_proxy = None
        # 如果配置代理
        if proxy:
            protocal = proxy.get("protocal", "socks5")
            proxy_ip = proxy.get("ip", "127.0.0.1")
            proxy_port = proxy.get("port", 7890)
            self.clash_proxy = f"{protocal}://{proxy_ip}:{proxy_port}"

    def start_requests(self):
        for category in CATEGORIES[::-1]:
            yield scrapy.Request(
                url=f"https://52fenhongbao.com/{category}",
                # url="https://52fenhongbao.com/forum/%E8%A5%BF%E5%AE%89%E9%AB%98%E6%96%B0%E9%81%87%E8%A7%81%E2%80%9C%E5%88%9D%E6%81%8B%E2%80%9D%E7%9A%84%E5%AE%8C%E7%BE%8E%E4%BD%93%E9%AA%8C-7c7b46256ed588c5eac406b4f7e4fc0e",
                callback=self.parse_detail,
                headers=HEADERS,
                # cookies=COOKIES,
                meta={"proxy": self.clash_proxy, "category": category},
            )

    def parse_detail(self, response):
        url = response.request.url
        category = response.request.meta.get("category", "")
        soup = BeautifulSoup(response.body, features="lxml")
        if category and "/forum/" in url:
            contact = soup.find_all("div", class_="mt1 mb1")[1].text
            if len(contact) > 100 and contact.count("回复") > 3:
                contact = ""
            yield {
                "uuid": url.split("-")[-1],
                "category": category,
                "name": soup.find_all("h4", class_="mt1 light")[0].text,
                "desc": soup.find_all("div", class_="mt1 mb1")[0].text,
                "contact": contact,
                "other": soup.find_all("tbody")[0].text,
                "time": soup.find_all("div", class_="d justify middle gap mt2")[0]
                .select("div.light")[0]
                .text,
                "city": soup.find_all("div", class_="mt1 mb1 light")[0].text,
                "imgs": [i.attrs["src"] for i in soup.find_all("img", alt="Image")],
            }
            return
        li = soup.select("a > div.left-item")

        for item in li:
            url = item.parent.attrs["href"]
            if url.startswith("/"):
                url = f"https://52fenhongbao.com{url}"
            if client.sismember("fl:fhb", url):
                continue
            cs = item.find_all("span", class_="marked")
            if cs:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_detail,
                    headers=HEADERS,
                    cookies=COOKIES,
                    meta={"proxy": self.clash_proxy, "category": cs[0].text},
                )
        is_find = False
        for a in soup.find_all("a", class_="button"):
            if is_find:
                try:
                    url = a.attrs["href"]
                except Exception as e:
                    logger.info(e)
                    break
                if not url.startswith("http"):
                    url = f"https://52fenhongbao.com/{url}"
                if client.sismember("fl:fhb", url):
                    break
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_detail,
                    headers=HEADERS,
                    cookies=COOKIES,
                    meta={"proxy": self.clash_proxy, "category": category},
                )
                break
            if "primary" in a.attrs["class"]:
                is_find = True
        client.sadd("fl:fhb", url)
        # self.sleep()

    def sleep(self):
        i = random.random()
        logger.info(f"sleep: {i}")
        time.sleep(i)
