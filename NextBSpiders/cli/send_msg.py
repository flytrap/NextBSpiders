import argparse
import asyncio
import base64
import json
import os
import random
import sys
import time

from loguru import logger

sys.path.insert(0, os.path.abspath("."))

from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB
from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs

MSG = "我刚刚创建了一个群组搜索机器人，叫做@gsearcher，欢迎大家来试用，并提供意见和反馈！"


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
        help="可指定多个配置文件，默认为空列表",
        type=str,
        dest="config",
        default="config.json",
    )
    parser.add_argument("-g", "--gid", help="指定组id", type=str, dest="gid", default="")

    args = parser.parse_args()

    return args


async def main(config_file: str, gid: str):
    with open(config_file, "r") as f:
        data = f.read()
    config_js = json.loads(data)
    proxy = config_js.get("proxy")
    # 如果配置代理
    clash_proxy = None
    if proxy:
        protocal = proxy.get("protocal", "socks5")
        proxy_ip = proxy.get("ip", "127.0.0.1")
        proxy_port = proxy.get("port", 7890)
        clash_proxy = (protocal, proxy_ip, proxy_port)
    telegram_app = TelegramAPIs()
    try:
        telegram_app.init_client(
            api_id=config_js["api_id"],
            api_hash=config_js["api_hash"],
            session_name=config_js["session_name"],
            proxy=clash_proxy,
            start=False,
        )
        telegram_app.client.start()
    except Exception as e:
        logger.exception(e)
    for user in telegram_app.get_chat_user(gid):
        telegram_app.send_msg(user, MSG)
        sleep()


def sleep():
    i = random.random() + random.randint(3, 60)
    logger.info(f"sleep: {i}")
    time.sleep(i)


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.config, args.gid))


if __name__ == "__main__":
    run()
