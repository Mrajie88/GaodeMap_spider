import requests
import time
import json
import pandas as pd
def pre_data():
    with open("./city.json", "r", encoding="utf") as f:
        city_info = json.load(f)
    adcode_list = []
    zhixiashi = ["11","12","31","50"]
    for i in range(len(city_info)):
        if (city_info[i]["adcode"][-4:] == "0000"):
            continue
        if ((city_info[i]["adcode"][-2:] == "00" ) or (city_info[i]["adcode"][-2:] == "01" and city_info[i]["adcode"][:2] not in zhixiashi)):
            continue
        adcode_list.append(city_info[i]["adcode"])
    return adcode_list
def main(adcode_list):
# 根据adcode_list 分别请求高德api
    tag = ""
    tag_list = []
    for item in adcode_list:
        tag = item
        url = geturl(item,0)
        # timeout (10,10)代表（connect timeout, read timeout）
        try:
            r = requests.get(url, timeout=(10,10))
            if(r.json()["info"]== "DAILY_QUERY_OVER_LIMIT"):
                print("配额不足")
                return -1
            count = r.json()["count"]
            page_num = (int(count) // 20) + 1
            temp = []
            for j in range(page_num):
                url1 = geturl(item,j)
                hotpot_list = requests.get(url1,timeout=(10,10)).json()["pois"]
                #处理获取的json数据
                process_data(hotpot_list,temp)
                # 控制爬取速度
                time.sleep(0.1)
            df = pd.DataFrame(temp,columns=["Name","City","distinct","address","cost","rating"])
            print(df)
            df.to_csv("hotpot_info.csv",encoding='utf_8_sig', index=False, header=False, mode='a+')
        except Exception as e:
            print("over-requests error:", e)
            tag_list.append(tag)
            tl = pd.DataFrame(tag_list)
            tl.to_csv("tl.csv")
            continue
def process_data(hotpot_list,temp):
    if(len(hotpot_list)!=0):
        for item in hotpot_list:
            if(item["name"]!=""):
                Name = item["name"]
            else:
                Name = "暂无"
            if(item["cityname"]!=""):
                city = item["cityname"]
            else:
                city = "暂无"
            if(item["adname"]!=""):
                distinct = item["adname"]
            else:
                distinct = "暂无"
            if(item["address"]!=""):
                address = item["address"]
            else:
                address = "暂无"
            if(item["biz_ext"]["cost"]!=""):
                cost = item["biz_ext"]["cost"]
            else:
                cost = "暂无"
            if(item["biz_ext"]["rating"]!=""):
                rating = item["biz_ext"]["rating"]
            else:
                rating = "暂无"
            temp.append([Name,city,distinct,address,cost,rating])
        return temp
    else:
        return
def geturl(item,page):
    url_base = "https://restapi.amap.com/v3/place/text?"
    web_key = "6d68f384822464c3daa9fb201931a10a"
    keywords = "火锅"
    city = str(item)  # adcode
    citylimit = str(True)
    url = url_base + "key=" + web_key + "&keywords=" + keywords + "&city=" + city + "&citylimit=" + citylimit + "&page=" + str(page)
    return url
if __name__=="__main__":
    adcode_list = pre_data()
    print(adcode_list.index("140722"))
    adcode_list = adcode_list[253:]
    main(adcode_list)
    #爬取失败的地区重新爬取
    adcode_list_sub = pd.read_csv("tl.csv").iloc[:,1].tolist()
    main(adcode_list_sub)