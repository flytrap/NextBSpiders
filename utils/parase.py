#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
# Created time: 2023/08/30
import re

import jieba


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
        li = re.findall("- ?(\d+\.?\d+?)", text)
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
