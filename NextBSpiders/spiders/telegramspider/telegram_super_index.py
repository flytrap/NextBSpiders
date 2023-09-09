#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
# Created time: 2023/08/30
import base64
import json
import os
import random
import time
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

            ls = [1]
            index = 0
            while index < len(ls):
                telegram_app.client.send_message(chat, "/lang")
                lang = list(telegram_app.client.get_messages(chat))[0]
                ls = [i for item in lang.buttons for i in item]

                bt = ls[index]
                logger.info(f"select lang: {bt.text}")
                self.sleep()
                try:
                    bt.click()
                except Exception as e:
                    logger.warning(e)
                    continue

                for item in self.iter_category_data(telegram_app, chat):
                    item["lang"] = bt.text
                    yield item
                index += 1
        except Exception as e:
            logger.exception(e)
        finally:
            telegram_app.close_client()

    def iter_category_data(self, telegram_app, chat, num=0) -> int:
        # 获取菜单
        index = 0
        ms = [1]
        while True:
            telegram_app.client.send_message(chat, "/tags")
            menus = list(telegram_app.client.get_messages(chat))
            if not menus:
                continue
            ms = [i for item in menus[-1].buttons for i in item]
            if index >= len(ms):
                return
            bt = ms[index]
            if bt.text in IGNORE_CATEGORIES:
                continue
            self.sleep()
            logger.info(f"select menu: {bt.text}")
            try:
                bt.click()
            except Exception as e:
                logger.warning(e)
                continue
            for item in self.get_massages(telegram_app, chat, bt.text):
                yield item
            index += 1

    def get_massages(self, telegram_app, chat, category: str):
        txt = ""
        while True:
            ms = list(telegram_app.client.get_messages(chat))
            if not ms:
                logger.info("nod found messages")
                return
            message = ms[0]
            if message.text == txt:
                break
            txt = message.text
            for m in ParseInfo.parse_items(message.text):
                m["category"] = category
                yield m
            bts = [i for item in message.buttons for i in item]
            ms = [i.text for i in bts]

            self.sleep()
            try:
                if "➡️ 下一页" in ms:
                    logger.info(f"click: 下一页")
                    bts[ms.index("➡️ 下一页")].click()
                    # message.click(ms.index("➡️ 下一页"))
                elif "➡️ Next" in ms:
                    logger.info(f"click: Next")
                    bts[ms.index("➡️ Next")].click()
                    # message.click(ms.index("➡️ Next"))
                else:
                    message.click(len(ms) - 1)
                    return
            except Exception as e:
                logger.warning(e)

    def set_lang(self, telegram_app, chat):
        telegram_app.client.send_message(chat, "/lang")
        for message in telegram_app.client.get_messages(chat):
            for index, bt in [i for item in message.buttons for i in item]:
                if bt.text == self.lang:
                    message.click(index)
                    break

    def sleep(self):
        i = random.random() + random.randint(1, 10)
        logger.info(f"sleep: {i}")
        time.sleep(i)
