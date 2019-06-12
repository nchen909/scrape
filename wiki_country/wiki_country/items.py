



# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiCountryItem(scrapy.Item):
    # define the fields for your item here like:
    label_num_dict=scrapy.Field()#排序完的结果 是一个列表！
    pass
