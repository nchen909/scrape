# -*- coding: utf-8 -*-
#上一行为了中文注释

#由于在缺陷中提到的那个乱码问题，我在\scrapy_country_and_label文件夹下顺便爬了国家和标签
import scrapy
import json
import time
import re

# def deal_luanma():
#     f = open('Americas-.txt','w+', encoding='utf-8')
#     res=(f.read().replace('聽', ' '))
#     f.write(res)
#     f.close()

class CountrySpider(scrapy.Spider):
    name = 'countryspider'
    def start_requests(self):
        with open(r'wiki_country/querys/input.json', 'r') as f:
            querys = json.load(f)#把国家load进来
        #print("###"+querys)
        path = 'http://en.wikipedia.org/wiki/'
        for query in querys['query']:
            url = path + '_'.join(query.split(' '))#对于比如United States去空格为_
            print(url)
            yield scrapy.Request(url=url ,callback=self.parse)#以parse方式发出request
#meta={'country_name':query}


    def parse(self, response):
        fields = response.css('.infobox').xpath('.//th[@scope="row"]')#infobox中获取标签如Area Population
        res = {}
        for field in fields:
            key = field.xpath('.//text()').extract_first()#对应一个个标签比如Area
            #' ' 是一种奇怪的空格？？？？？？？？？？？？？？？/怎么办
            value = field.xpath('string(../td)').extract_first().replace('\xa0', ' ')
            #string可以解决有很多值 把所有值都提取
            #获取标签对应值，比如Area是4254900m平方米 如果有空格符就换成一般空格
            value = re.sub(r'\[(\d{1,2})\]','',value)
            #维基会有类似论文中的上标表示出处，将其删去
            res[key] = value#res生成关于infobox标签的键值对'
        f = open(r'wiki_country/querys/fields.txt',encoding='utf-8')
        #ff='Area,Population,GDP (nominal),HDI,Demonym,Countries,Languages,Time zones'
        field_set = f.read().split(',')#读入标签并分割成集合
        #field_set = ff.split(',')
        country_name = response.css('.firstHeading::text').extract_first()#大标题 也就是国家名字
        #timestamp= str(int(time.time()))#获取系统时间
        res_path=r'wiki_country/results'
        f_name=res_path+'\\'+country_name+'.txt'#要导入结果的文件名
        fw = open(f_name, 'w',encoding='utf-8')#覆盖写
        fw.write('CountryName')
        fw.write('#' + '#'.join(field_set) + '\n')#把标签献给文件
        fw.write(country_name)
        for field in field_set[:]:#准备写值
            fw.write('#')
            if field in res:#有值就写没值就过
                fw.write(res[field].replace('\n',''))#多行的可能会有\n
        fw.close()
        f.close()