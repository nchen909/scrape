# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class WikiCountryPipeline(object):
    #def __init__(self):
     #   self.filename = open(r'wiki_country/querys/fields.txt','w+', encoding='utf-8')#因为写的列表，所以覆盖写

    def process_item(self, item, spider):
        #if item['label']:
        #    self.filename.write(item['label']+',')
        #self.filename.close()
        #f2 = open(r'wiki_country/querys/fields.txt', 'w+', encoding='utf-8')#覆盖写

        # for label_ in item['label_num_dict']:
        #     self.filename.write(label_ + ',')
        if spider.name=='label':
            filename = open(r'wiki_country/querys/fields.txt', 'w+', encoding='utf-8')#因为写的列表，所以覆盖写
            count = 0
            for tuple_ in item['label_num_dict']:
                filename.write(str(tuple_[0]))
                count+=1
                if count>40:#取前40个输出
                    break
                else:
                    filename.write(',')
            filename.close()
        #field_set = self.filename.read().split(',')[:-1]#去掉最后一个逗号的空的

        return item

    #def close_spider(self,spider):#只在所有爬完的时候才运行
        #filename = open(r'wiki_country/querys/fields.txt', 'w+', encoding='utf-8')
        #取前四十个的字段输出并结束
        #field_set = listself.filename.read()
        #count=0

        #self.filename.close()
        #下面 吃掉最后一个逗号
        # self.filename = open(r'wiki_country/querys/fields.txt', 'w+', encoding='utf-8')
        # field_set = self.filename.read()[:-1]
        # self.filename.write(field_set)
        # self.filename.close()
