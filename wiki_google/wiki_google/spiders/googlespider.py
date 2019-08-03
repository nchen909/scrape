# -*- coding: utf-8 -*-
#由于scrapy开出来的界面与实际完全不一样 甚至在windows和CentOS开出来也不一样 所以一切以scrapy爬出来的实际结果为准
import scrapy
import json
import time
import random
import re
from ..items import WikiGoogleItem
#from ..getProxy import get_ip_list,get_proxies,getHTMLText
class GooglespiderSpider(scrapy.Spider):
    name = 'googlespider'
    #allowed_domains =['www.google.com']
    # def __init__(self):
    #     self.pagenow=''
    #     self.page = 1
    def start_requests(self):
        with open(r'wiki_google/querys/input.json', 'r') as f:
            querys = json.load(f)
        id=1#第几个query
        for query in querys['query']:
            pre_query=query#用来当文件名输出
            ###HTML ASCII Reference
            new_query=''
            for alpha in query:
                o=ord(alpha)
                if (o >= 33 and o <= 47) or (o >= 58 and o <= 64) or (o >= 91 and o <= 96) or (o >= 123 and o <= 126):
                    new_query+=hex(o).replace('0x','%')
                else:
                    new_query+=alpha
            query = new_query.replace(' ','+')
            ###
            path = 'https://www.google.com/search?q=%s&hl=en' % query#因为服务器开出来的是english版本 所以爬english的
            # 若直接用谷歌的任意其中一个IP地址172.217.14.78会报Invalid DNS-ID（如果robot设成true直接报错终止 设成false会报warning ）是因为scrapy官方库没写好罢了
            # 当初一直坚持用IP 甚至导致本地windows crawl的时候没response是因为要统一windows和云服务器CentOS那边的界面 方便调试
        #把CentOS的DNS手动改成8.8.8.8
            yield scrapy.Request(url=path,meta={'query': query,'pre_query':pre_query,'id':id,'page':{id:1}},callback=self.parse)#  # 下一个要执行的函数为parse
            id+=1

    def parse(self, response):
        query = response.meta['query']
        pre_query=response.meta['pre_query']
        id=response.meta['id']
        page=response.meta['page']
        fields = response.xpath('.//div[@class="ZINbbc xpd O9g5cc uUPGi"]')
        page_value=page[id]

        res_path = r'wiki_google/results'
        f_name = res_path + '/' + str(id) + '_' + pre_query + '_page'+ str(page_value)+ '.txt'  # 要导入结果的文件名
        fw = open(f_name, 'w', encoding='utf-8')  # 覆盖写
        fw.write('key#title#content#url\n')

        for field in fields:
            # 考虑到最开始会有视频 还有一些小标签之类的 要把所有信息提出来 所以分类讨论
            #所谓的视频标签和正常小块等等的区别 在于标题的class是BNeawe vvjwJb AP7Wnd还是BNeawe deIvCb AP7Wnd
            #或者有左右的滚轮或者没有左右滚轮（如球队啊视频啊之类的）即len(content_list)是否=2
            content_list=field.xpath('..//div[@class="BNeawe s3v9rd AP7Wnd"]')
            if (len(content_list)==2):#不是滚轮
                title = field.xpath('..//div[@class="BNeawe vvjwJb AP7Wnd"]/text()').extract_first()
                if not(title):
                    title = field.xpath('..//div[@class="BNeawe deIvCb AP7Wnd"]//text()').extract_first()
                #不排除的确是滚轮但是只有两项的情况
                if(title):#不是视频和标签之类 是正常的一个小块
                    content = content_list[0].xpath('string(.)').extract_first()#把�换成/!!! 不需要换了 浏览器那显示�只不过是本地编码的问题
                    #url = field.xpath('..//div[@class="BNeawe UPmit AP7Wnd"]/text()').extract_first().replace(' › ', '/')#把>换成/!!!
                    url = 'https://www.google.com' + field.xpath('..//a//@href').extract_first().replace(' › ', '/')
                    #print(title,content,url,'\n')用于调试
                    #这里结果中会有些一条内容占多行 用str将其拉成一行
                    #fw.write('#' + str(title) + '#' + str(content) + '#' + str(url) + '\n') 如果不要一行 保留原来空格 把str去了就是
                else:#是标签
                    title=field.xpath('..//div[@class="BNeawe deIvCb AP7Wnd"]/text()').extract_first()
                    content = content_list[0].xpath('string(.)').extract_first()  # 把�换成/!!!
                    url = 'https://www.google.com'+field.xpath('..//a//@href').extract_first().replace(' › ', '/')
                fw.write(pre_query)
                # try:
                fw.write('#' + str(title) + '#' + str(content) + '#' + str(url) + '\n')
                # except:
                #     print('#######title:', title, '\n')
                #     print('#######content:', content, '\n')
                #     print('#######url:', url, '\n')
                #     return
            elif len(content_list)==0:#比如republic of china里的Top stories
                title=field.xpath('..//div[@class="BNeawe deIvCb AP7Wnd"]//text()').extract_first()
                titles=field.xpath('..//div[@class="BNeawe deIvCb AP7Wnd"]//text()').extract()[1:]
                content_list = field.xpath('..//a[@class="tHmfQe"]')
                for content_ in content_list:
                    content = content_.xpath('string(..//div[@class="BNeawe deIvCb AP7Wnd"])').extract_first().replace('\n', '')
                    url = 'https://www.google.com' + content_.xpath('.//@href').extract_first()
                    fw.write(pre_query)
                    fw.write('#' + str(title) + '#' + str(content) + '#' + str(url) + '\n')
            else:#在首页的视频里边
                content_list=field.xpath('..//a[@class="BVG0Nb"]')
                title = field.xpath('..//div[@class="BNeawe deIvCb AP7Wnd"]//text()').extract_first()
                if not(title):
                    title = field.xpath('..//div[@class="BNeawe vvjwJb AP7Wnd"]/text()').extract_first()
                #不排除title是非首页最上方title的滚轮情况
                content_exist=field.xpath('..//div[@class="BNeawe wyrwXc AP7Wnd"]')#比如PEOPLE ALSO SEARCH FOR 等标签
                if not(content_exist):#无标签  就正常的最前面的那种大标签
                    for content_ in content_list:
                        content = content_.xpath('string(.)').extract_first().replace('\n', '')
                        url = 'https://www.google.com' + content_.xpath('.//@href').extract_first()
                        fw.write(pre_query)
                        # try:
                        fw.write('#' + str(title) + '#' + str(content) + '#' + str(url) + '\n')
                        # except:
                        #     print('#######title:',title,'\n')
                        #     print('#######content:', content, '\n')
                        #     print('#######url:', url, '\n')
                        #     return
                else:#有比如PEOPLE ALSO SEARCH FOR / TEAMS 之类标签
                    block_without_title=field.xpath('..//div[@class="xpc"]')
                    long_content=''
                    iters=block_without_title.xpath('.//div[contains(@class,"jfp3ef")]')
                    key=0#决定是内容还是下面的滚轮
                    for iter in iters:
                        is_label=iter.xpath('./span/div[@class="BNeawe wyrwXc AP7Wnd"]')
                        if key==0:
                            if not(is_label):
                                long_content +=iter.xpath('string(.)').extract_first()
                            else:
                                key=1
                                content=long_content
                                url = 'https://www.google.com' + field.xpath('.//@href').extract_first()
                                fw.write(pre_query)
                                fw.write('#' + str(title) + '#' + str(content) + '#' + str(url) + '\n')
                                title = iter.xpath('string(.)').extract_first()#第一次key=1的title
                        else:
                            if is_label:
                                title = iter.xpath('string(.)').extract_first()
                            else:
                                content=iter.xpath('string(.)').extract_first().replace('\n', '')
                                url = 'https://www.google.com' + iter.xpath('../../../../a//@href').extract_first()
                                fw.write(pre_query)
                                fw.write('#' + str(title) + '#' + str(content) + '#' + str(url) + '\n')


        page_value+=1

        fw.close()
        if page_value==6:
            print('#############################################################\n')
            #self.crawler.engine.close_spider(self, 'scrape %s in google for 5 page successfully!' % query)
            print('scrape %s in google for 5 page successfully!' % pre_query)
            print('#############################################################\n')
            return
        next_page=response.xpath('//a[@aria-label="Next page"]//@href').extract_first()
        if not(next_page):
            print('#############################################################\n')
            print('scrape %s in google for %d page successfully!\nthis query has only %d page!\n'%(pre_query,page_value-1,page_value-1))
            print('#############################################################\n')
            return
        else:
            pagenow_value = 'https://www.google.com'+next_page

        yield scrapy.Request(url=pagenow_value, meta={'query': query,'pre_query':pre_query,'id':id,'page':{id:page_value}}, callback=self.parse)
        time.sleep(random.random() * 5)

