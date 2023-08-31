#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
# Created time: 2023/08/30
import base64
import json
import os
from abc import ABC

import scrapy
from loguru import logger

from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs

from utils.parase import ParseInfo

IGNORE_CATEGORIES = ["↩️ 返回"]


class TelegramSuperIndex(scrapy.Spider, ABC):
    name = "telegramSuperIndex"  # 超级索引爬取

    # 降低效率，单线程，每个请求延迟4秒
    custom_settings = {"CONCURRENT_REQUESTS": 4, "DOWNLOAD_DELAY": 1}

    def __init__(self, param, **kwargs):
        super().__init__(**kwargs)
        s_param = base64.b64decode(param).decode()
        self.param = json.loads(s_param)
        self.api_id = self.param.get("api_id")
        self.api_hash = self.param.get("api_hash")
        self.session_name = self.param.get("session_name")
        self.chat_code = self.param.get("chat_code")
        self.lang = self.param.get("lang")  # 设置语言
        self.category_tag = "🏷 标签"
        proxy = self.param.get("proxy")
        self.clash_proxy = None
        # 如果配置代理
        if proxy:
            protocal = proxy.get("protocal", "socks5")
            proxy_ip = proxy.get("ip", "127.0.0.1")
            proxy_port = proxy.get("port", 7890)
            self.clash_proxy = (protocal, proxy_ip, proxy_port)

    def start_requests(self):
        yield scrapy.Request(url="https://baidu.com", callback=self.parse_list)

    def parse_list(self, response):
        if not os.path.exists(self.session_name):
            logger.warning("session not exists.")
            return
        yield from self.scan_messages()

    def scan_messages(self):
        telegram_app = TelegramAPIs()
        try:
            telegram_app.init_client(
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_name=self.session_name,
                proxy=self.clash_proxy,
            )
        except Exception as e:
            logger.warning(e)
            return None
        try:
            # 开始爬取
            chat = telegram_app.get_entity(self.chat_code)
            if self.lang:  # todo: 更新语言
                telegram_app.client.send_message(chat, "/lang")

            telegram_app.client.send_message(chat, self.category_tag)
            for menu in telegram_app.client.get_messages(chat):
                # 获取菜单
                for index, bt in enumerate([i for item in menu.buttons for i in item]):
                    if bt.text in IGNORE_CATEGORIES:
                        continue
                    menu.click(index)
                    for item in self.get_massages(telegram_app, chat, bt.text):
                        yield item
        except Exception as e:
            logger.exception(e)
        finally:
            telegram_app.close_client()

    def get_massages(self, telegram_app, chat, category: str):
        while True:
            for message in telegram_app.client.get_messages(chat):
                for m in ParseInfo.parse_items(message.text):
                    m["category"] = category
                    yield m
                ms = [i.text for item in message.buttons for i in item]
                if "➡️ 下一页" not in ms:
                    return
                message.click(ms.index("➡️ 下一页"))
