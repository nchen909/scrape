# -*- coding: utf-8 -*-
import scrapy
import json
#import time
import re


class CountrySpider(scrapy.Spider):
    name = 'countryspider'
    def start_requests(self):
        path = 'https://www.worldometers.info/geography/alphabetical-list-of-countries/'
        yield scrapy.Request(url=path ,callback=self.parse)#以parse方式发出request
#meta={'country_name':query}


    def parse(self, response):
        countrys = response.xpath('//td[@style="font-weight: bold; font-size:15px"]/text()').extract()
        input_='{"query":['
        for country in countrys:
            #print('###########'+country)
            input_=input_+'"'+'_'.join(country.split(' ')).replace('\xa0', ' ')+'",'
        input_=input_[:-1]+']}'
        f_name='./wiki_country/querys/input.json'
        fw = open(f_name, 'w',encoding='utf-8')#覆盖写
        fw.write(input_)
        fw.close()