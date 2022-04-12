# 要統測了我為甚麼要寫這個東西
# 別問了 瑟瑟是人類第一動力
import gevent.monkey
gevent.monkey.patch_all()
import requests
import grequests
import os
import re
from fake_useragent import UserAgent
import threading
import json

#sys.setrecursionlimit(10000)
def check():
    if not os.path.isdir("images"):
        os.mkdir("images")
    if not os.path.isfile("set.json"):
        f=open("set.json","w")
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
    r= requests.get(url[0],stream=True,headers=headers)
    image = "images/" + str(url[2]) +".jpg"
    with open(image,"wb") as f:
        print("save")
        f.write(r.content)


def download2(urls):
    durls = []
    ct = 0
    for i in urls:
        durls.append(f"https://i.loli.best/{i[1]}")
    rs = (grequests.get(url) for url in durls)
    responses = grequests.map(rs, size = 5)
    for response in responses:
        try:
            image = "images/" + str(urls[ct][2]) +".jpg"
            with open(image,"wb") as f:
                print(f"save {urls[ct][2]} done")
                f.write(response.content)
                ct += 1
        except:
            image = "images/" + str(urls[ct][2]) +"1.jpg"
            with open(image,"wb") as f:
                print(f"save {urls[ct][2]} done")
                f.write(response.content)
                ct += 1



def main():
    userid = input("Please enter userid: ")
    now = 0
    with open("set.json","r") as f:
        data = json.load(f)
        cookiee = data["cookie"]

    cookie = {i.split("=")[0]:i.split("=")[1] for i in cookiee.split("; ")} 
    # cookies = data[0]
    # cookie = {i.split("=")[0]:i.split("=")[-1] for i in cookies.split("; ")}
    while True:
        ua = UserAgent()  
        user_agent = ua.random

        headers = {
                    'user-agent': user_agent,
                    'referer': 'https://www.pixiv.net',
                    "cookie": cookiee

                }
        images = requests.get("https://www.pixiv.net/ajax/user/"+str(userid)+"/illusts/bookmarks?tag=&offset="+str(now)+"&limit=48&rest=show&lang=zh_tw",headers=headers,cookies=cookie)
        #images = requests.get("http://www.pixiv.net/ajax/user/33573448/illusts/bookmarks?tag=&offset=0&limit=48&rest=show&lang=zh_tw",headers=headers,cookies=cookie)
        works = images.json()

        works = works["body"]["works"]

        if works == []:
            print("[done] No more works")
            break
        urls = []
        for work in works:
            urls.append((re.sub("/c/250x250_80_a2","",re.sub("p0_square","p0_master",work["url"])),work["id"],re.sub('[\/:*?"<>|]','-',work["title"])))
        # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        #     executor.map(download, urls)
        t = threading.Thread(target=download2(urls))
        t.start()
        #download2(urls)
        #break
        now += 48


if __name__ == '__main__':
    check()
    main()