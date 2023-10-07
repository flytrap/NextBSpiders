import argparse
import asyncio
import base64
import json
import os
import random
import sys
import time

from loguru import logger
from redis import Redis

sys.path.insert(0, os.path.abspath("."))

from NextBSpiders import NEXTBSPIDER_VERSION
from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB
from NextBSpiders.spiders.telegramspider.telegramAPIs import TelegramAPIs

MSG = "[hi, 您好, 新建了一个群组搜索机器人, 帮助您更快的找到您需要的群组:快搜，欢迎试用！](http://t.me/gsearcher)"

client = Redis("192.168.3.13", db=1)


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


def main(config_file: str, gid: str):
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
        )
    except Exception as e:
        logger.exception(e)
    for user in telegram_app.get_chat_user(gid):
        if user.is_self:
            continue
        if user.bot:
            continue
        if user.deleted:
            continue
        if client.sismember("msg:sended", user.id):
            continue
        try:
            logger.info(f"send msg: {user.username}")
            telegram_app.send_msg(user, MSG)
            client.sadd("msg:sended", user.id)
        except Exception as e:
            logger.warning(e)
            time.sleep(60 * 60)
        sleep()
    telegram_app.close_client()


def sleep():
    i = random.random() + random.randint(30, 300)
    logger.info(f"sleep: {i}")
    time.sleep(i)


def run():
    """
    CLI命令行入口
    """
    args = parse_cmd()
    loop = asyncio.get_event_loop()
    main(args.config, args.gid)


if __name__ == "__main__":
    run()
