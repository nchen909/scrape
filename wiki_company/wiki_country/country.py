# -*- coding: utf-8 -*-
import scrapy
import json
#import time
import re


class CountrySpider(scrapy.Spider):
    name = 'countryspider'
    def start_requests(self):
        path = 'https://en.wikipedia.org/wiki/List_of_company_name_etymologies'#维基官网的没有地域等限制的公司列表 非常齐全
        yield scrapy.Request(url=path ,callback=self.parse)#以parse方式发出request
#meta={'country_name':query}


    def parse(self, response):
        countrys = response.xpath('//li/a[@href and @title]//@href').extract()
        input_='{"query":['
        for country in countrys:
            #print('###########'+country)
            input_=input_+'"'+'_'.join(country.split(' ')).replace('\xa0', ' ')+'",'
        input_=input_[:-1]+']}'
        f_name='./wiki_country/querys/input.json'
        fw = open(f_name, 'w',encoding='utf-8')#覆盖写
        fw.write(input_)
        fw.close()