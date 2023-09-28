import asyncio
import os
import sys
from loguru import logger
from grpclib.client import Channel

sys.path.insert(0, os.path.abspath("."))

from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB
from utils.parase import ParseInfo
from NextBSpiders.bot_api.tg_grpc import TgBotServiceStub
from NextBSpiders.bot_api.tg_pb2 import DataItem, DataInfo

group_map = {
    1147972019: "SE-索引秘书",
    1186432626: "群联索引",
    1187088309: "超级索引",
    1794489809: "超级索引",
}
HOST = "192.168.0.102"
PORT = 7011


async def update_message_data(tp="message"):
    async with Channel(HOST, PORT) as channel:
        greeter = TgBotServiceStub(channel)

        items = []
        async for item in get_messages(tp):
            items.append(
                DataInfo(
                    category=item["category"] if item.get("category") else "",
                    detail=DataItem(
                        type=item.get("type", 0),
                        name=item["name"],
                        desc=item.get("desc", ""),
                        number=item.get("number", 0),
                        code=item["code"],
                        language=item.get("lang", "chinese").split()[-1].lower()
                        if item.get("lang")
                        else "chinese",
                    ),
                    tags=item.get("tags", []),
                )
            )
            if len(items) >= 10000:
                reply = await greeter.ImportData(items)
                print(len(reply))
                items = []
        if items:
            reply = await greeter.ImportData(items)
            print(len(reply))


async def get_messages(tp="message"):
    nb = NextBTGPOSTGRESDB()

    if tp == "group":
        data = nb.get_group_data()
        for item in data:
            info = dict(item)
            info["tags"] = item.tags.split(",")
            info["category"] = item.category.split()[-1].lower()
            yield info
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
    loop.run_until_complete(update_message_data("group"))


if __name__ == "__main__":
    main()
