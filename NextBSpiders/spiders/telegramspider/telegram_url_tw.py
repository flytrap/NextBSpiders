from abc import ABC

import scrapy
from bs4 import BeautifulSoup

base_url = "https://www.telegram.url.tw"


class TelegramScanMessages(scrapy.Spider, ABC):
    name = "telegram.url.tw"

    # 降低效率，单线程，每个请求延迟4秒
    custom_settings = {"CONCURRENT_REQUESTS": 4, "DOWNLOAD_DELAY": 1}
    start_urls = [
        base_url,
        "https://www.telegram.url.tw/HongKong/index.html",
        "https://www.telegram.url.tw/China/index.html",
    ]

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.body, features="lxml")
        if "category" in response.meta:
            category = response.meta["category"]
            ols = soup.find_all("ol")
            if ols:
                for a in ols[0].find_all("a"):
                    url = a.attrs["href"]
                    if "joinchat" in url:
                        continue
                    yield {
                        "code": url.split("/")[-1],
                        "name": a.text,
                        "category": category,
                        "type": 1,
                    }
                if len(ols) > 1:
                    for ol in ols[1:]:
                        url = a.attrs["href"]
                        if "joinchat" in url:
                            continue
                        for a in ol.find_all("a"):
                            yield {
                                "code": url.split("/")[-1],
                                "name": a.text,
                                "category": category,
                                "type": 2,
                            }
            # yield self.parse_detail(soup, response.meta["category"])
            return
        uls = soup.find_all("ul", class_="dropdown-menu")
        for ul in uls:
            for a in ul.find_all("a"):
                yield scrapy.Request(
                    f"{base_url}/{a.attrs['href']}", meta={"category": a.text}
                )
        print(uls)

    def parse_detail(self, soup: BeautifulSoup, category: str):
        ols = soup.find_all("ol")
        if ols:
            for a in ols[0].find_all("a"):
                url = a.attrs["href"]
                if "joinchat" in url:
                    continue
                yield {
                    "code": url.split("/")[-1],
                    "name": a.text,
                    "category": category,
                    "type": 1,
                }
            if len(ols) > 1:
                for ol in ols[1:]:
                    url = a.attrs["href"]
                    if "joinchat" in url:
                        continue
                    for a in ol.find_all("a"):
                        yield {
                            "code": url.split("/")[-1],
                            "name": a.text,
                            "category": category,
                            "type": 2,
                        }
