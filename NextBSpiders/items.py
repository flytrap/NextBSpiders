# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime, BIGINT, Integer

Base = declarative_base()


class TelegramMessage(Base):
    __tablename__ = "nextb_telegram_messages"

    # postgresql
    id = Column(BIGINT(), primary_key=True, unique=True, autoincrement=True)
    # sqlite
    # id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    message_id = Column(BIGINT())
    chat_id = Column(BIGINT())
    user_id = Column(BIGINT())
    user_name = Column(String(255))
    nick_name = Column(String(255))
    postal_time = Column(DateTime)
    reply_to_msg_id = Column(BIGINT())
    from_name = Column(String(255))
    from_time = Column(DateTime)
    message = Column(String(5096))
    text = Column(String(5096))


class TelegramGroupInfo(Base):
    __tablename__ = "nextb_telegram_group"

    # postgresql
    id = Column(BIGINT(), primary_key=True, unique=True, autoincrement=True)

    name = Column(String(255))
    code = Column(String(255))  # 群代号
    lang = Column(String(255))  # 语言
    category = Column(String(255))
    type = Column(Integer())  # 区分群组还是channel
    number = Column(Integer())
    desc = Column(Text())
    tags = Column(String(5096))  # 逗号分割


class TelegramGroupExtend(Base):
    __tablename__ = "telegram_group_extend"

    # postgresql
    id = Column(BIGINT(), primary_key=True, unique=True, autoincrement=True)

    name = Column(String(255))
    code = Column(String(255))  # 群代号
    lang = Column(String(255))  # 语言
    type = Column(Integer())  # 区分群组还是channel
    number = Column(Integer())
    active = Column(Integer())  # 活跃人数
    desc = Column(Text())
    is_delete = Column(Boolean())


class FenHongBao(Base):
    __tablename__ = "fl_fhb"

    # postgresql
    id = Column(BIGINT(), primary_key=True, unique=True, autoincrement=True)

    uuid = Column(String(255))
    name = Column(String(512))
    category = Column(String(512))
    city = Column(String(512))  # 城市分级
    time = Column(String(256))  # 发布时间
    contact = Column(String(512))  # 联系方式
    desc = Column(Text())
    other = Column(Text())
    imgs = Column(Text())  # 图片json
