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
        path = 'http://en.wikipedia.org'
        for query in querys['query']:
            url = path + query
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
