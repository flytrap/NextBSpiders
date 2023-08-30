import os
import sys

import pymysql

sys.path.insert(0, os.path.abspath("."))

from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB
from utils.parase import ParseInfo

db = pymysql.connect(
    host="192.168.0.102", user="flytrap", passwd="flytrap", database="telegram-bot"
)

cursor = db.cursor()
group_map = {
    1147972019: "SE-索引秘书",
    1186432626: "群联索引",
    1187088309: "超级索引",
    1794489809: "超级索引",
}


def get_or_create_tag(tag: str) -> int:
    cursor.execute(f"select id from tg_tag where name = '{tag}'")
    data = cursor.fetchone()
    if not data:
        cursor.execute(f"insert into tg_tag(name) values ('{tag}')")
        db.commit()
        return cursor.lastrowid
    return data[0]


def get_or_create_category(category: str) -> int:
    cursor.execute(f"select id from tg_category where name = '{category}'")
    data = cursor.fetchone()
    if not data:
        cursor.execute(f"insert into tg_category(name) values ('{category}')")
        db.commit()
        return cursor.lastrowid
    return data[0]


def check_txt(txt: str) -> str:
    if "'" in txt:
        return f'"{txt}"'
    else:
        return f"'{txt}'"


def main():
    nb = NextBTGPOSTGRESDB()

    data = nb.get_messages()
    for item in data:
        f = getattr(ParseInfo, f"parse_{item.chat_id}", None)
        if not f:
            f = ParseInfo.parse_items
        try:
            results = f(item.text)
        except Exception as e:
            print(e)
            continue
        if isinstance(results, dict):
            results = [results]
        for result in results:
            if result and "code" in result:
                cid = 0
                if result.get("category"):
                    cid = get_or_create_category(result["category"])
                code = check_txt(result["code"])
                cursor.execute(f"select id from tg_group where code={code}")
                data = cursor.fetchone()
                if data:
                    continue
                name = check_txt(result["name"])
                desc = check_txt(result.get("desc", ""))
                tp = result.get("type", 1)
                num = result.get("number", 0)
                sql = f"insert into tg_group(`name`,`code`,`desc`,`category`,`type`,`number`) values({name},{code},{desc},{cid},{tp},{num})"
                try:
                    cursor.execute(sql)
                except Exception as e:
                    print(e)
                    cursor.execute(
                        f"insert into tg_group(`name`,`code`,`category`,`type`,`number`) values({name},{code},{cid},{tp},{num})"
                    )
                db.commit()
                group_id = cursor.lastrowid
                for tag in result["tags"]:
                    tid = get_or_create_tag(tag)
                    sql = f"insert into tg_group_tag(tag_id,group_id) values({tid},{group_id})"
                    try:
                        cursor.execute(sql)
                        db.commit()
                    except Exception as e:
                        print(e)


if __name__ == "__main__":
    main()
