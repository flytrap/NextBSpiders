import asyncio
import json
import os
import ssl
import sys
from datetime import datetime
import grpclib

from grpclib.client import Channel
from loguru import logger
from redis import Redis

sys.path.insert(0, os.path.abspath("."))

from NextBSpiders.bot_api.tg_grpc import TgBotServiceStub
from NextBSpiders.bot_api.tg_pb2 import DataInfo, DataItem
from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB
from utils.parase import ParseInfo

HOST = "127.0.0.1"
PORT = 7011

client = Redis("192.168.3.13", db=1)
redis_key = "grpc:fhb"

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations("NextBSpiders/bot_api/server.pem")
context.check_hostname = False
# ssl.get_default_verify_paths()._replace(cafile="NextBSpiders/bot_api/server.pem")


async def update_message_data(tp="message"):
    client.delete(redis_key)
    async with Channel(HOST, PORT, ssl=context) as channel:
        greeter = TgBotServiceStub(channel)

        items = []
        async for item in get_messages(tp):
            ts = 0
            if item.get("time"):
                ts = datetime.strptime(item["time"].strip(), "%Y-%m-%d").timestamp()
            imgs = json.loads(item.get("imgs", ""))
            key = f"{item['name']}:{item.get('type', 0)}:{item.get('desc', '')}:{item.get('private', '')}:{ts}:{len(imgs)}"
            if client.sismember(redis_key, key):
                continue
            items.append(
                DataInfo(
                    category=item["category"] if item.get("category") else "",
                    detail=DataItem(
                        type=item.get("type", 0),
                        name=item["name"].strip(),
                        desc=item.get("desc", "").strip(),
                        number=item.get("number", 0),
                        code=item.get("code", item["uuid"]),
                        language=item.get("lang", "chinese").split()[-1].lower()
                        if item.get("lang")
                        else "chinese",
                        extend=item.get("other", "").strip(),
                        private=item.get("contact", "").strip(),
                        location=item.get("city", "").strip(),
                        time=int(ts),
                        images=imgs,
                    ),
                    tags=item.get("tags", []),
                )
            )
            client.sadd(redis_key, key)
            if len(items) >= 1000:
                reply = await greeter.ImportData(items)
                print(len(reply))
                items = []
        if items:
            reply = await greeter.ImportData(items)
            print(len(reply))
        client.delete(redis_key)


async def get_messages(tp="message"):
    nb = NextBTGPOSTGRESDB()

    if tp == "group":
        data = nb.get_group_data()
        for item in data:
            info = dict(item)
            info["tags"] = item.tags.split(",")
            info["category"] = item.category.split()[-1].lower()
            yield info
    elif tp == "fhb":
        data = nb.get_fhb_data()
        for item in data:
            yield item.__dict__
    else:
        data = nb.get_messages()
        for item in data:
            f = getattr(ParseInfo, f"parse_{item.chat_id}", None)
            if not f:
                f = ParseInfo.parse_items
            try:
                results = f(item.text)
            except Exception as e:
                logger.info(e)
                continue
            if isinstance(results, dict):
                results = [results]
            for result in results:
                if result and "code" in result:
                    if result.get("category"):
                        if not result["category"].startswith("top:"):
                            result["category"] = result["category"].split()[-1].lower()
                    yield result


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_message_data("fhb"))


if __name__ == "__main__":
    main()
