import os
import re
import sys

import pymysql
import jieba

sys.path.insert(0, os.path.abspath("."))

from NextBSpiders.libs.nextb_spier_db import NextBTGPOSTGRESDB

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


class ParseInfo(object):
    @classmethod
    def parse_1147972019(cls, text: str):
        li = text.split("\n")
        result = {"tags": []}
        for i, item in enumerate(li):
            names = re.findall("\[(.*)\]", item)
            if not names:
                continue
            if "标题" in item:
                result["name"] = names[0]
                result["code"] = re.findall("\((.*)\)", item)[0].split("/")[-1]
            elif "标签" in item:
                result["tags"] = re.findall("#(\w+)\s?", item)
            elif "分类" in item:
                result["category"] = item.split()[-1].strip()
            elif "简介" in item:
                result["desc"] = "\n".join(li[i + 1 :])
        if "code" not in result:
            return {}

        if "category" in result:
            result["tags"].append(result["category"])
        result["tags"] += [
            item.strip()
            for item in jieba.cut(result["name"])
            if item.strip() and cls.check_tag(item.strip())
        ]
        result["tags"] = list(set(result["tags"]))

        return result

    @classmethod
    def parse_items(cls, text: str):
        li = text.split("\n")
        results = []
        for i, item in enumerate(li):
            if not cls.check_group(item):
                continue
            result = {}
            name = re.findall("\[(.*)\]", item)[0].replace("/", "")
            result["name"] = (
                "-".join(name.split("-")[:-1]).strip() if "-" in name else name
            )
            result["code"] = re.findall("\((.*)\)", item)[0].split("/")[-1]
            result["tags"] = list(
                set(
                    [
                        item.strip()
                        for item in jieba.cut(result["name"])
                        if item.strip() and cls.check_tag(item.strip())
                    ]
                )
            )
            result["type"] = 2 if "📢" in item else 1
            try:
                result["number"] = cls.parse_number(name)
            except Exception as e:
                print(e)
            results.append(result)

        return results

    @staticmethod
    def check_group(item: str) -> bool:
        if len(item) < 10:
            return False
        if not item or item.startswith("[广告]"):
            return False
        if "📢" not in item and "👥" not in item:
            return False
        if "🔥📢" in item:
            return False
        return True

    @staticmethod
    def parse_number(text: str) -> int:
        """解析数字"""
        li = re.findall("- ?(\d+)", text)
        if not li:
            return 0
        if text.lower().endswith("k"):
            return int(li[-1]) * 1000
        elif text.lower().endswith("m"):
            return int(li[-1]) * 1000000
        return int(li[-1])

    @staticmethod
    def check_tag(text: str) -> bool:
        return re.match("\w+", text)


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
