# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import scrapy

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import exists

from NextBSpiders.configs.postgreconfig import db_config
from NextBSpiders.items import TelegramMessage, TelegramGroupInfo

"""
后续需要将所有的输出结果统一到一个pipeline里，根据爬虫选择输出方式
"""


class AppspiderPostgreslPipeline(object):
    def __init__(self):
        self.template_conn_str = (
            "postgresql+psycopg2://{username}:{password}@{address}:{port}/{db_name}"
        )
        self.conn_str = self.template_conn_str.format(**db_config)
        self.session_maker = None
        self.datas = []
        self.push_number = 50

    def open_spider(self, spider: scrapy.Spider):
        engine = create_engine(self.conn_str)
        if self.session_maker is None:
            self.session_maker = scoped_session(
                sessionmaker(autoflush=True, autocommit=False, bind=engine)
            )

    def process_item(self, item, spider: scrapy.Spider):
        if len(self.datas) >= self.push_number:
            if spider.name == "telegram.url.tw":
                self.save_group_info()
            else:
                self.save_datas()
        else:
            if item:
                self.datas.append(item)
        return item

    def close_spider(self, spider: scrapy.Spider):
        if len(self.datas) > 0:
            if spider.name == "telegram.url.tw":
                self.save_group_info()
            else:
                self.save_datas()
        self.session_maker.close_all()

    def save_datas(self):
        for data in self.datas:
            message_id = data.get("message_id", -1)
            chat_id = data.get("chat_id", -1)
            is_exist = self.session_maker.query(
                exists().where(
                    TelegramMessage.message_id == message_id,
                    TelegramMessage.chat_id == chat_id,
                )
            ).scalar()
            if is_exist:
                continue
            new_message = TelegramMessage()
            new_message.message_id = message_id
            new_message.chat_id = chat_id
            new_message.user_id = data.get("user_id", -1)
            new_message.user_name = data.get("user_name", "")
            new_message.nick_name = data.get("nick_name", "")
            new_message.postal_time = data.get("postal_time")
            new_message.reply_to_msg_id = data.get("reply_to_msg_id", -1)
            new_message.from_name = data.get("from_name", "")
            new_message.from_time = data.get("from_time")
            new_message.message = data.get("message", "")
            new_message.text = data.get("text", "")
            self.session_maker.add(new_message)
        self.session_maker.commit()
        self.datas = []

    def save_group_info(self):
        for data in self.datas:
            code = data.get("code", "")
            if not code:
                continue
            is_exist = self.session_maker.query(
                exists().where(TelegramGroupInfo.code == code)
            ).scalar()
            if is_exist:
                continue
            new_message = TelegramGroupInfo()
            new_message.code = code
            new_message.name = data.get("name", "")
            new_message.category = data.get("category", "")
            new_message.type = data.get("type", 1)
            new_message.number = data.get("number", 0)
            new_message.desc = data.get("desc", "")
            new_message.tags = ",".join(data.get("tags", []))
            self.session_maker.add(new_message)
        self.session_maker.commit()
        self.datas = []


class AppspiderTxtPipeline(object):
    def open_spider(self, spider):
        self.file = open(spider.name + ".txt", "a")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class AppspiderSqlitePipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        # Here, you get whatever value was passed through the "db_name" parameter
        settings = crawler.settings
        db_name = settings.get("db_name")

        # Instantiate the pipeline with your table
        return cls(db_name)

    def __init__(self, db_name):
        self.conn_str = "sqlite:///{db_name}".format(db_name=db_name)
        self.session_maker = None
        self.datas = []
        self.push_number = 50

    def open_spider(self, spider):
        engine = create_engine(self.conn_str)
        if self.session_maker is None:
            self.session_maker = scoped_session(
                sessionmaker(autoflush=True, autocommit=False, bind=engine)
            )

    def process_item(self, item, spider):
        if len(self.datas) >= self.push_number:
            for data in self.datas:
                new_message = TelegramMessage()
                new_message.message_id = data.get("message_id", -1)
                new_message.chat_id = data.get("chat_id", -1)
                new_message.user_id = data.get("user_id", -1)
                new_message.user_name = data.get("user_name", "")
                new_message.nick_name = data.get("nick_name", "")
                new_message.postal_time = data.get("postal_time")
                new_message.reply_to_msg_id = data.get("reply_to_msg_id", -1)
                new_message.from_name = data.get("from_name", "")
                new_message.from_time = data.get("from_time")
                new_message.message = data.get("message", "")
                new_message.text = data.get("text", "")
                self.session_maker.add(new_message)
            self.session_maker.commit()
            self.datas = []
        else:
            if item:
                self.datas.append(item)
        return item

    def close_spider(self, spider):
        if len(self.datas) > 0:
            for data in self.datas:
                new_message = TelegramMessage()
                new_message.message_id = data.get("message_id", -1)
                new_message.chat_id = data.get("chat_id", -1)
                new_message.user_id = data.get("user_id", -1)
                new_message.user_name = data.get("user_name", "")
                new_message.nick_name = data.get("nick_name", "")
                new_message.postal_time = data.get("postal_time")
                new_message.reply_to_msg_id = data.get("reply_to_msg_id", -1)
                new_message.from_name = data.get("from_name", "")
                new_message.from_time = data.get("from_time")
                new_message.message = data.get("message", "")
                new_message.text = data.get("text", "")
                self.session_maker.add(new_message)
            self.session_maker.commit()
            self.datas = []
        self.session_maker.close_all()


class AppspiderMongoPipeline(object):
    def open_spider(self, spider):
        self.file = open(spider.name + ".txt", "a")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
