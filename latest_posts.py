# encoding: utf-8

import os
import sys
import time
import json
from urllib2 import urlopen

from to_room import XMPPBot


def main(password):
    rerun = False

    if os.path.exists("db.json"):
        try:
            db = json.load(open("db.json"))
        except Exception:
            rerun = True
            db = {"post_ids": []}
    else:
        db = {"post_ids": []}

    with XMPPBot(password, room="forum") as bot:
        raw_categories = json.load(urlopen("https://forum.yunohost.org/site.json"))["categories"]
        categories = {x["id"]: x["name"] for x in raw_categories}

        for category in raw_categories:
            if "parent_category_id" in category:
                categories[category["id"]] = categories[category["parent_category_id"]] + "/" + category["name"]

        for post in reversed(json.load(urlopen("https://forum.yunohost.org/posts.json"))["latest_posts"]):
            if post["id"] in db["post_ids"]:
                continue
            else:
                db["post_ids"].append(post["id"])

            category = categories[post["category_id"]]
            title = post["topic_title"]
            user = post["username"]
            url = "https://forum.yunohost.org/t/%s/%s/%s" % (post["topic_slug"], post["topic_id"], post["post_number"])

            extract = post["raw"].replace("\n", " ")
            if len(extract) > 200:
                extract = extract[:200] + "..."

            to_send = u'[%s] « %s » @%s: %s %s' % (category, title, user, extract, url)

            print(to_send.encode("utf-8"))

            # on rerun don't resend everything, we might miss a post but it's
            # better than spaming
            # better solution would be to avoid posting things older than last
            # modified time of db.json but I don't have the time to do that
            # right now
            if not rerun:
                bot.sendToChatRoom(to_send)
                time.sleep(3)

    # split operations in case dumps fail and I don't want to break the file
    db = json.dumps(db)
    open("db.json", "w").write(db)


if __name__ == '__main__':
    if not len(sys.argv[1:]):
        print("Usage : python latest_posts.py <password>")
        sys.exit(1)

    password = sys.argv[1]
    main(password)
