#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
# Created time: 2023/09/22
import base64
import json
import random
import time
from abc import ABC
from typing import List

import scrapy
from loguru import logger

from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs

IGNORE_CATEGORIES = ["↩️ 返回"]


class TelegramGroupUpdate(scrapy.Spider, ABC):
    name = "telegramGroupUpdate"  # 获取群组信息

    # 降低效率，单线程，每个请求延迟4秒
    custom_settings = {"CONCURRENT_REQUESTS": 4, "DOWNLOAD_DELAY": 1}

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
            self.clash_proxy = (protocal, proxy_ip, proxy_port)

    def start_requests(self):
        with open("codes.txt") as f:
            codes = f.readlines()
        for item in self.scan_messages(codes):
            yield item

    def scan_messages(self, codes: List[str]):
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
            return
        try:
            # 开始爬取
            for code in codes:
                logger.info(f"get chat: {code}")
                chat = telegram_app.get_info(code.strip())
                yield chat
                self.sleep()
        except Exception as e:
            logger.exception(e)
        finally:
            telegram_app.close_client()

    def sleep(self):
        i = random.random() + random.randint(1, 10)
        logger.info(f"sleep: {i}")
        time.sleep(i)
