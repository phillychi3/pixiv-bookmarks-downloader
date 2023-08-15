# 要統測了我為甚麼要寫這個東西
# 別問了 瑟瑟是人類第一動力
import gevent.monkey
gevent.monkey.patch_all()
import json  # noqa: E402
import threading  # noqa: E402
from fake_useragent import UserAgent  # noqa: E402
import re  # noqa: E402
import os  # noqa: E402
import requests  # noqa: E402
import queue  # noqa: E402

def check():
    if not os.path.isdir("images"):
        os.mkdir("images")
    if not os.path.isfile("set.json"):
        f = open("set.json", "w")
        f.write(r'{"cookie":""}')
        f.close()
        print("please set your cookie in set.json")
        exit()


def download(url):
    ua = UserAgent()
    user_agent = ua.random
    headers = {
        'user_agent': user_agent,
        'referer': f"https://www.pixiv.net/artworks/{url[1]}"
    }
    r = requests.get(url[0], stream=True, headers=headers)
    image = "images/" + str(url[2]) + ".jpg"
    # with open(image,"wb") as f:
    #     print("save")
    #     f.write(r.content)
    with open(image, 'wb') as f:
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)

def thread_download(q, whoami):
    while True:
        try:
            data = q.get(block=False, timeout=4)
            if data['mulitpage']:
                url = f"https://i.loli.best/{data['id']}/{data['nowpage']}"
                print(
                    f"doenload[{whoami}] is downlaoding {data['title']}-{data['nowpage']}")
                r = requests.get(url)
                try:
                    image = "images/" + str(data["title"]) + \
                        '-' + str(data['nowpage']) + ".jpg"
                    with open(image, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            if chunk:
                                f.write(chunk)
                except:
                    image = "images/" + str(data["title"]) + \
                        '-' + str(data['nowpage']) + "r.jpg"
                    with open(image, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            if chunk:
                                f.write(chunk)
            else:
                url = f"https://i.loli.best/{data['id']}"
                print(f"doenload[{whoami}] is downlaoding {data['title']}")
                r = requests.get(url)
                try:
                    image = "images/" + str(data["title"]) + ".jpg"
                    with open(image, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            if chunk:
                                f.write(chunk)
                except:
                    image = "images/" + str(data["title"]) + "r.jpg"
                    with open(image, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            if chunk:
                                f.write(chunk)
            q.task_done()
        except queue.Empty:
            break


def main():
    userid = input("Please enter userid: ")
    now = 0
    with open("set.json", "r") as f:
        data = json.load(f)
        cookiee = data["cookie"]

    cookie = {i.split("=")[0]: i.split("=")[1] for i in cookiee.split("; ")}
    # cookies = data[0]
    # cookie = {i.split("=")[0]:i.split("=")[-1] for i in cookies.split("; ")}
    thequeue = queue.Queue()
    while True:
        # ua = UserAgent()
        # user_agent = ua.random

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'referer': 'https://www.pixiv.net/users/',
            'Accept-Encoding': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            "cookie": cookiee
        }
        images = requests.get("https://www.pixiv.net/ajax/user/"+str(userid)+"/illusts/bookmarks?tag=&offset=" +
                              str(now)+"&limit=48&rest=show&lang=zh_tw", headers=headers, cookies=cookie)
        works = images.json()

        works = works["body"]["works"]

        if works == []:
            print("[done] No more works")
            break

        for work in works:
            downdata = {
                "url": (re.sub("/c/250x250_80_a2", "", re.sub("p0_square", "p0_master", work["url"]))),
                "id": work["id"],
                "title": re.sub('[\/:*?"<>|]', '-', work["title"]),
                "mulitpage": False if work["pageCount"] == 1 else True,
                "nowpage": 0
            }
            if work["pageCount"] == 1:
                thequeue.put(downdata)

            else:
                for nowpage in range(0, work["pageCount"]):
                    nnowpage = downdata.copy()
                    nnowpage["nowpage"] = nowpage
                    thequeue.put(nnowpage)

        now += 48

    for ctthread in range(0, 5):
        t = threading.Thread(target=thread_download, args=(thequeue, ctthread))
        t.start()

    thequeue.join()


if __name__ == '__main__':
    check()
    main()