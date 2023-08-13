# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 15:24:23
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : telegram_create_table.py
# @Software : Visual Studio Code
# @WeChat   : NextB


__doc__ = """
创建telegram消息表
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB, NextBTGSQLITEDB


def parse_cmd():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog="nextb-telegram-create-table",
        description="NextBSpider创建telegram数据表。版本号：{}".format(NEXTBSPIDER_VERSION),
        epilog="使用方式：nextb-telegram-create-table -c $config_file",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="设置爬虫配置文件",
        type=str,
        dest="config",
        action="store",
        default="./config.json",
    )

    args = parser.parse_args()

    return args


def telegram_create_table(config_file):
    # 加载配置文件
    with open(config_file, "r") as f:
        data = f.read()
    config_js = json.loads(data)
    if config_js.get("db_type") == "postgres":
        nb = NextBTGPOSTGRESDB()
    else:
        nb = NextBTGSQLITEDB(db_name=config_js.get("sqlite_db_name", "tg_sqlite.db"))
    nb.create_table()


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    telegram_create_table(args.config)


if __name__ == "__main__":
    run()
