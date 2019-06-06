# -*- coding: utf-8 -*-
# @Author: 潘晓宇
# @Date:   2018-11-16 10:08:32

from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
#import time
#import random
import pinyin

my_headers=[
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
]

headers = {
    'x-devtools-emulate-network-conditions-client-id': "5f2fc4da-c727-43c0-aad4-37fce8e3ff39",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'dnt': "1",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.8,en;q=0.6",
    'cookie': "__c=1501326829; lastCity=101020100; __g=-; __l=r=https%3A%2F%2Fwww.google.com.hk%2F&l=%2F; __a=38940428.1501326829..1501326829.20.1.20.20; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1501326839; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1502948718; __c=1501326829; lastCity=101020100; __g=-; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1501326839; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1502954829; __l=r=https%3A%2F%2Fwww.google.com.hk%2F&l=%2F; __a=38940428.1501326829..1501326829.21.1.21.21",
    'cache-control': "no-cache",
    'postman-token': "76554687-c4df-0c17-7cc0-5bf3845c9831"
}


urlHeader = 'https://hz.lianjia.com/ershoufang'
csvFilename = 'ershoufang.csv'
ignoreList =['桐庐', '淳安', '建德'] 

itemKeys = [
    'title'     ,
    'location'  ,
    'brief'     ,
    'style'     ,
    'follow'    ,
    'price tot' ,
    'price unit'   
]

item = {
    'title'     :   '',
    'location'  :   '',
    'brief'     :   '',
    'style'     :   '',
    'follow'    :   '',
    'price tot' :   '',
    'price unit':   ''
}


# save
def save(csvFile, item):

    #print(item)

    for itemKeyIndex in range(len(itemKeys)):
        csvFile.write(item[itemKeys[itemKeyIndex]].replace(',', ' ') + ',')
    csvFile.write('\n')



# from url get html
def gethtml(url):

    print(url)

    # random user-agent to avoid 403
    # headers['user-agent'] = random.choice(my_headers)
    html = requests.get(url, headers=headers)
    if html.status_code != 200: # 爬的太快网站返回403，这时等待解封吧
        print('status_code is %d' % html.status_code)
    soup = BeautifulSoup(html.text, "html.parser")

    return soup


def main(): 

    locationMemory = {}
    
    csvFile = open(csvFilename,'w', encoding='utf-8')
    exceptionListFile = open('exception', 'w', encoding='utf-8')

    # write column headers
    for eleKey in itemKeys:
        csvFile.write(eleKey + ',')
    csvFile.write('\n')

    #############
    ## Prepare ##
    #############
    # get all location
    districtSoup = gethtml(urlHeader)
    # get districts at first
    districts = districtSoup.find('div', 'position').find_all('dl')[1].dd.div.get_text(' ').split()
    # get locations in each districts
    for district in districts:
        # don't wanna leave too far away
        if (district in ignoreList):
            continue

        locationMemory[district] = []
        # get the pinyin of all districts
        district_pinyin = pinyin.get(district, format='strip')
        # construct url
        urlDistrict = urlHeader+'/'+district_pinyin
        # get locations
        locationSoup = gethtml(urlDistrict)
        locations = locationSoup.find('div', 'position').find_all('dl')[1].dd.div.find_all('div')[1].find_all('a')
        # put locations into memory
        for location in locations:
            locationMemory[district] += [location.get_text('') + ':' + location['href']]

    ###############
    ## Main Work ##
    ###############
    locationPassed = []
    # iterate locations
    for district in locationMemory.keys():
        locations = locationMemory[district]
        for location in locations:
            try:
                # there are some repeated locations
                if (location.split(':')[0] in locationPassed):
                    exceptionListFile.write(district + "   " + location + '   ' + 'repeat' + '\n')
                    continue
                else:
                    locationPassed += [location.split(':')[0]]
                item['location'] = district + '-' + location.split(':')[0]
                # construct url
                urlLocation = urlHeader + '/' + location.split(':')[1].split('/')[2]
                # get how many pages there are for each location
                pageSoup = gethtml(urlLocation)
                maxPage = int(pageSoup.find('div', 'page-box fr').div['page-data'].split(',')[0].split(':')[1])
                # if maxPag > 50, there may be some problems
                # if (maxPage > 50):
                #    exceptionListFile.write(district + "   " + location + '   ' + 'page error' + '\n')
                #    continue
    
                # iterate to get house list on each page
                for page in range(maxPage):
                    # page start from 1
                    page = page + 1
                    #construct url
                    urlPage = urlLocation + '/pg' + str(page)
                    # get house list
                    listSoup = gethtml(urlPage)
                    houses = listSoup.find('ul', 'sellListContent').find_all('li')
                    # iterate to get house infos
                    for house in houses:
                        info = house.find('div', 'info clear')
                        # title
                        title = info.find('div', 'title').get_text()
                        # brief
                        brief = info.find('div', 'address').get_text()
                        # style
                        style = info.find('div', 'flood').get_text()
                        # follow
                        follow = info.find('div', 'followInfo').get_text()
                        # price
                        priceTotal = info.find('div', 'totalPrice').get_text()
                        priceUnit  = info.find('div', 'unitPrice').get_text()
                        
                        # save infos
                        item['title'     ] = title
                        item['brief'     ] = brief
                        item['style'     ] = style
                        item['follow'    ] = follow
                        item['price tot' ] = priceTotal
                        item['price unit'] = priceUnit
                        save(csvFile, item)
            except Exception as e:
                exceptionListFile.write(str(e) + district + "   " + location + '\n')
                continue

    csvFile.close()
    exceptionListFile.close()

                    

if __name__ == "__main__":
    main()
