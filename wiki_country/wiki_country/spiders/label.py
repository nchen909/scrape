# -*- coding: utf-8 -*-
import scrapy
import json
#import time
import re
from ..items import WikiCountryItem
class LabelSpider(scrapy.Spider):
    name = 'label'
    def __init__(self):

        self.items={}

    def start_requests(self):
        with open(r'wiki_country/querys/input.json', 'r') as f:
            querys = json.load(f)  # 把国家load进来
        path = 'http://en.wikipedia.org/wiki/'
        for query in querys['query']:
            url = path + '_'.join(query.split(' '))  # 对于比如United States去空格为_
            print(url)
            yield scrapy.Request(url=url, callback=self.parse)  # 以parse方式发出request

    def parse(self, response):
        fields = response.css('.infobox').xpath('.//tr[not(contains(@class, "mergedrow") or contains(@class, "mergedbottomrow"))]/th[@scope="row"]')
        # infobox中获取标签如Area Population 不能含比如'• 4th Republic of Albania'的子标题
        #res = {}
        for field in fields:
            item=WikiCountryItem()
            key = field.xpath('.//text()').extract_first().replace('\xa0', ' ')  # 对应一个个标签比如Area
            if key not in self.items:
                self.items[key]=1
                #以此去重 若在字典里就不再加一遍
            else:
                self.items[key]+=1
            #print('self.items:',self.items)
            #item['label_num_dict']=sorted(self.items.keys())
            item['label_num_dict'] =sorted(self.items.items(), key=lambda item: item[1], reverse=True)#按出现多少的顺序输出
            yield item
            #print("item['label_num_dict']",item['label_num_dict'])# #把标签多的放在前面输出 这是一个列表！
            # # ' ' 是一种奇怪的空格？？？？？？？？？？？？？？？/怎么办
            # value = field.xpath('string(../td)').extract_first().replace('\xa0', ' ')
            # # string可以解决有很多值 把所有值都提取
            # # 获取标签对应值，比如Area是4254900m平方米 如果有空格符就换成一般空格
            # value = re.sub(r'\[(\d{1,2})\]', '', value)
            # # 维基会有类似论文中的上标表示出处，将其删去
            # res[key] = value  # res生成关于infobox标签的键值对'
        # f = open(r'wiki_country/querys/fields.txt')
        # # ff='Area,Population,GDP (nominal),HDI,Demonym,Countries,Languages,Time zones'
        # field_set = f.read().split(',')  # 读入标签并分割成集合
        # # field_set = ff.split(',')
        # country_name = response.css('.firstHeading::text').extract_first()  # 大标题 也就是国家名字
        # # timestamp= str(int(time.time()))#获取系统时间
        # res_path = r'wiki_country/results'
        # f_name = 'fields.txt'  # 要导入结果的文件名
        # fw = open(f_name, 'w', encoding='utf-8')  # 覆盖写
        # fw.write('#' + 'Country')
        # fw.write('#' + '#'.join(field_set) + '\n')  # 把标签献给文件
        # fw.write('#' + country_name)
        # for field in field_set[:]:  # 准备写值
        #     fw.write('#')
        #     if field in res:  # 有值就写没值就过
        #         fw.write(res[field].replace('\n', ''))  # 多行的可能会有\n
        # fw.close()
        #f.close()
