# -*- coding: utf-8 -*-
# @Author: 潘晓宇
# @Date:   2019-04-04 10:08:32

filename = 'ershoufang.csv'
dstFileName = 'blocks.csv'


def grep(filename):
    
    blocksNames = {};
    
    ershoufangFile = open(filename, 'r', encoding='utf-8')

    for line in ershoufangFile:

        items = line.split(',')
        if (len(items) != 8 or items[0] == 'title'):
            continue

        district = items[1].strip().split('-')
        if (len(district) != 2):
            continue

        brief = items[2].strip()
        price = int(items[6].strip()[2:-4])
        items = brief.split('|')
        if (len(items) != 6):
            continue
        block = items[0].strip()

        if not block in blocksNames:
            blocksNames[block] = [district[0], district[1], 1, float(price)]
        else:
            count = blocksNames[block][2]
            average = blocksNames[block][3]
            average = (average * count + price) / (count + 1)
            blocksNames[block][2] += 1
            blocksNames[block][3] = average
            
    ershoufangFile.close()

    return blocksNames 


def main():

    blocksNames = grep(filename)
    
    dstFile = open(dstFileName, 'w', encoding='utf-8')
    for key in blocksNames.keys():
        dstFile.write(key + ',')
        for value in blocksNames[key]:
            dstFile.write(str(value) + ',')
        dstFile.write('\n')
    
    dstFile.close()


if __name__ == "__main__":
    main();
