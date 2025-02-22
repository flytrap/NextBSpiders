# -*- coding: utf-8 -*-
# @Time     : 2022/11/16 11:02:47
# @Author   : ddvv
# @Site     : https://ddvvmmzz.github.io
# @File     : nextb_spier_db.py
# @Software : Visual Studio Code
# @WeChat   : NextB


from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import scoped_session, sessionmaker

from NextBSpiders.configs.postgreconfig import db_config
from NextBSpiders.items import Base, TelegramMessage, TelegramGroupInfo, FenHongBao


class NextBTGSQLITEDB:
    def __init__(self, db_name):
        """
        初始化对象
        """
        self.engine = self.init_db_connection(db_name)
        self.session_maker = None
        self.create_session()

    @staticmethod
    def init_db_connection(db_name):
        """
        链接数据库
        """
        conn_str = "sqlite:///{db_name}".format(db_name=db_name)
        engine = create_engine(conn_str)
        return engine

    # DRbmfj86yJ3sqv21X5fo9A
    def create_session(self):
        """
        创建数据库链接
        """
        if self.session_maker is None:
            self.session_maker = scoped_session(
                sessionmaker(autoflush=True, autocommit=False, bind=self.engine)
            )

    def close(self):
        """
        关闭数据库链接
        """
        self.session_maker.close_all()
        self.engine.dispose()

    # 创建表
    def create_table(self):
        """
        初始化数据表
        """
        Base.metadata.create_all(self.engine)

    def get_first_one_message(self):
        """
        获取最早一条消息
        """
        data = (
            self.session_maker.query(TelegramMessage)
            .order_by(TelegramMessage.id.asc())
            .limit(1)
        )
        if data.count():
            return data[0]
        else:
            return None

    def get_last_one_message(self, chat_id=None):
        """
        获取最近一条消息
        """
        q = self.session_maker.query(TelegramMessage)
        if chat_id:
            q = q.filter(TelegramMessage.chat_id == chat_id)

        data = q.order_by(TelegramMessage.id.desc()).limit(1)
        if data.count():
            return data[0]
        else:
            return None

    def get_messages(self, begin_offset_date=None, end_oofset_date=None):
        """
        获取消息，用于统计用户每天的发言数目
        begin_offset_date: 查询时间的起始偏移，默认查询最早的时间
        end_offset_date: 查询时间的结束偏移，默认查询当前的时间
        """
        q = self.session_maker.query(
            TelegramMessage.user_id,
            TelegramMessage.nick_name,
            TelegramMessage.postal_time,
            TelegramMessage.chat_id,
            TelegramMessage.text,
        )
        if begin_offset_date and end_oofset_date:
            datas = q.filter(
                TelegramMessage.postal_time >= begin_offset_date,
                TelegramMessage.postal_time < end_oofset_date,
            ).all()
        else:
            datas = q.all()
        for data in datas:
            yield data

    def get_group_data(self):
        q = self.session_maker.query(
            TelegramGroupInfo.name,
            TelegramGroupInfo.code,
            TelegramGroupInfo.lang,
            TelegramGroupInfo.category,
            TelegramGroupInfo.type,
            TelegramGroupInfo.number,
            TelegramGroupInfo.desc,
            TelegramGroupInfo.tags,
        )
        for data in q.all():
            yield data

    def get_fhb_data(self):
        q = self.session_maker.query(FenHongBao)

        for data in q.all():
            yield data

    def get_user_distinct_count(self):
        """
        统计用户数量
        """
        data = self.session_maker.query(distinct(TelegramMessage.user_id))
        return data.count()

    def get_message_count(self):
        """
        统计消息数量
        """
        data = self.session_maker.query(TelegramMessage.id)
        return data.count()


class NextBTGPOSTGRESDB(NextBTGSQLITEDB):
    def __init__(self):
        """
        初始化对象
        """
        self.engine = self.init_db_connection()
        self.session_maker = None
        self.create_session()

    @staticmethod
    def init_db_connection():
        """
        链接数据库
        """
        template_conn_str = (
            "postgresql+psycopg2://{username}:{password}@{address}:{port}/{db_name}"
        )
        conn_str = template_conn_str.format(**db_config)
        engine = create_engine(conn_str)
        return engine
