# -*- coding: utf-8 -*-
# @Author: 潘晓宇
# @Date:   2018-11-16 10:08:32

from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
#import time
#import random
import pinyin
import grepBlocks

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


urlHeader = 'https://hz.lianjia.com/zufang/rt200600000001rs'
csvFilename = 'zushoubi.csv'


# save
def save(csvFile, block, values):

    #print(item)
    csvFile.write(block + ',')
    for value in values:
        csvFile.write(str(value) + ',')
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
    exceptionListFile = open('exception2', 'w', encoding='utf-8')

    #############
    ## Prepare ##
    #############
    blocks = grepBlocks.grep('ershoufang.csv')
    
    ###############
    ## Main Work ##
    ###############
    for block in blocks.keys():
        urlBlock = urlHeader + block + '/'
        blockSoup = gethtml(urlBlock)
       
        rentAverage = 0
        rentSumPrice = 0
        rentSumArea = 0
        count = 0

        ## @note, only grep the first page now
        houses = blockSoup.find_all('div', 'content__list--item--main')
        for house in houses:
            try:
                area  = house.find('p', 'content__list--item--des').get_text()
                area = area.strip().replace(' ', '').replace('/', '').replace('\n', ',').split(',')[2]
                if '㎡' not in area:
                    continue
                area = int(area[0:-1])

                price = house.find('span', 'content__list--item-price').get_text().strip()
                if '元/月' not in price:
                    continue
                price = int(price[0:-4])
                
                rentSumPrice += price
                rentSumArea  += area 
                count += 1
                
            except Exception as e:
                exceptionListFile.write(str(e) + block + '\n')
                continue

        if rentSumArea > 0:
            rentAverage = rentSumPrice / rentSumArea
        
        print(rentAverage)
        blocks[block] += [count, rentAverage]

        save(csvFile, block, blocks[block])
    
    csvFile.close()
            

if __name__ == "__main__":
    main()


