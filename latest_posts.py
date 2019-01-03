import os
import sys
import json
from urllib.request import urlopen

from to_room import XMPPBot


def main(password):
    if os.path.exists("db.json"):
        db = json.load(open("db.json"))
    else:
        db = {"post_ids": []}

    raw_categories = json.load(urlopen("https://forum.yunohost.org/site.json"))["categories"]
    categories = {x["id"]: x["name"] for x in raw_categories}

    for category in raw_categories:
        if "parent_category_id" in category:
            categories[category["id"]] = f'{categories[category["parent_category_id"]]}/{category["name"]}'

    for post in json.load(urlopen("https://forum.yunohost.org/posts.json"))["latest_posts"]:
        if post["id"] in db["post_ids"]:
            continue
        else:
            db["post_ids"].append(post["id"])

        category = categories[post["category_id"]]
        title = post["topic_title"]
        user = post["username"]

        extract = post["raw"].replace("\n", " ")
        if len(extract) > 200:
            extract = extract[:200] + "..."

        to_send = f'[{category}] @{user} on "{title}": {extract}'

        print(to_send)

        with XMPPBot(password, room="forum") as bot:
            bot.sendToChatRoom(to_send)

    json.dump(db, open("db.json", "w"))


if __name__ == '__main__':
    if not len(sys.argv[1:]):
        print("Usage : python latest_posts.py <password>")
        sys.exit(1)

    password = sys.argv[1]
    main(password)
