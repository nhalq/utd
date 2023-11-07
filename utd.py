#!/usr/bin/python3

import json
import os
import requests
import sqlite3

from bs4 import BeautifulSoup
from datetime import datetime


class Agent:
    def collect(self):
        raise NotImplementedError("NOT_IMPLEMENT")


class HCMUSAgent(Agent):
    def collect(self):
        # response = requests.get("https://sdh.hcmus.edu.vn/thong-bao-cao-hoc/")
        # data = response.text

        with open("playground/hcmus", "r") as fs:
            data = "".join(fs.readlines())

        soup = BeautifulSoup(data, "html.parser")
        updates = soup.select("#category-posts-REPLACE_TO_ID-internal > li")

        for update in updates:
            title_tag, time_tag = update.children
            link_tag, _ = title_tag.children

            yield dict({
                "title": title_tag.get_text().strip(),
                "ref": link_tag["href"].strip(),
                "timestamp": HCMUSAgent.unix_timestamp(time_tag.get_text().strip())
            })

    @staticmethod
    def unix_timestamp(s):
        py_timestamp = datetime.strptime(s, "%d/%m/%Y %I:%M %p")
        return datetime.timestamp(py_timestamp)


if __name__ == "__main__":
    fn = "data/higher-education.json"

    records = list()
    lastest_record = None

    if os.path.exists(fn):
        with open(fn, "r") as fs:
            records = json.load(fs)
        lastest_record = records[0]

    agent = HCMUSAgent()
    new_records = list(agent.collect())
    for num_updates, new_record in enumerate(new_records):
        if new_record == lastest_record:
            break

    if num_updates:
        print("We have", num_updates, "update(s)")
        update_records = new_records[:num_updates]
        for record in update_records:
            print("-", record["title"])

        records = update_records + records
        with open(fn, "w") as fs:
            json.dump(records, fs, indent=2)
