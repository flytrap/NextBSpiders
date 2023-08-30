# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 15:24:41
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : telegram_run_spider.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
NextBSpider执行telegram爬虫命令行工具
"""

import argparse
import base64
import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from scrapy import cmdline
from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB

scrapy_cfg = """# Automatically created by: scrapy startproject
#
# For more information about the [deploy] section see:
# https://scrapyd.readthedocs.io/en/latest/deploy.html

[settings]
default = NextBSpiders.settings
"""


def process_scrapy_cfg_file():
    current_dir = os.path.abspath(".")
    scrapy_file = os.path.join(current_dir, "scrapy.cfg")
    if not os.path.exists(scrapy_file):
        with open(scrapy_file, "w") as f:
            f.write(scrapy_cfg)
            f.flush()


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="run-spider",
        description="NextBSpider执行telegram爬虫命令行工具。{}".format(NEXTBSPIDER_VERSION),
        epilog="使用方式：nextb-telegram-run-spider -c $config_file1 -c $config_file2",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="设置爬虫配置文件，可指定多个配置文件，默认为空列表",
        type=str,
        dest="config",
        default="config.json",
    )
    parser.add_argument(
        "-n", "--name", help="指定爬虫名称", type=str, dest="name", default="telegram.url.tw"
    )

    args = parser.parse_args()

    return args


def telegram_run_spider(config_file: str, name: str):
    # 加载配置文件
    with open(config_file, "r") as f:
        data = f.read()
    config_js = json.loads(data)
    # 初始化数据库
    # nb = NextBTGPOSTGRESDB()
    # nb.create_table()

    # base64配置参数，传递给爬虫
    param_base64 = base64.b64encode(json.dumps(config_js).encode()).decode()
    cmd = f"scrapy crawl {name} -L INFO -a param={param_base64}"

    cmdline.execute(cmd.split())
    # os.system(cmd)


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    process_scrapy_cfg_file()
    telegram_run_spider(args.config, args.name)


if __name__ == "__main__":
    run()
