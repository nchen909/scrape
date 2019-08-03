# 爬谷歌的README：https://github.com/1012598167/scrapy-wikipedia-country/tree/master/wiki_google


# scrapy wikipedia country

## 实验目的

### 爬虫实习的项目1，利用python的scrapy框架爬取维基百科（英文）说的国家信息。



## 实验要求

- 1. 网址：<https://en.wikipedia.org/> 
  2. 描述：根据用户输入国家名称搜索，爬取结果页面中国家信息。
  3. 输入：国家名称。
  4. 输出：国家信息。
  5. 字段：国家名称#Motto#Anthem#National song#Capital#Largest city#...#Internet TLD#更多信息。
  6. 要求：字段比较不统一，除上述字段外，请先搜索几十个主要国家，看下包含哪些字段，把最大字段集合确定下来，然后开始写爬虫。某国家不存在某字段，则该字段为空字符串。调研后可以与我讨论字段集合。



## 实验过程

- ```shell
  conda install scrapy
  ```

  

- 选择一个文件夹，打开poweshell

- ```shell
  mkdir internship\ spider\ scrapy
  cd internship\ spider\ scrapys
  scrapy startproject wiki_country
  scrapy genspider countryspider
  scrapy list#看有没有生成这个spider 结果有countryspider
  ```

  在result中有wiki.py

- 之后在wiki_country文件下放querys和results文件存输入和输出

  

## 文件目录

![路径](https://github.com/1012598167/my-tuchuang/raw/master/1560350953127.png)



第一个子文件是github仓库，第二个是scrapy的文件目录格式。

## 中间过程

本来只有一个wiki.py就行了，但是因为一些手动输入标签会产生一些乱码：

**小部分可以使用.replace()函数，并且将编码设置为与网站源码相同，比如 #coding:utf-8**

**然后对于一些‘GDP (nominal)’（wiki Americas的标签）这中间这个空格会在utf-8下出现各种形式，比如‘ ’（\xa0）,' '(\xc2\xa0),'聽'('\xe8\x81\xbd'),'鑱?'('\xe9\x91\xb1?'),一种在不同软件的utf-8打开会改变utf-8编码甚至切换成斜体的空格：**



```json
Area,Population,GDP (nominal),HDI,Demonym,Countries,Languages,Time zones
```

如这边的'GDP (nominal)'(标签产生于<https://en.wikipedia.org/wiki/Americas>)中的空格，就是上述类型的空格，您可以试着爬该网站的标签至json文件，发现其空格与之后Time zones的空格完全不等长。

**解决：可以初步尝试打开这个输出结果并重新replace一下，再f.close()，也可以试着直接爬下标签（或国家名）之后再爬对应的值，省去中间步骤，即不要自己输键而把键也直接爬下来（标签/国家名）。**

所以我试着自己从头爬国家，爬标签并且爬值（对应三个spider）。

同时我用了三种写法写着三个spider：

- 爬国家：单个py文件使用scripy runspider country.py就可直接当成spider crawl

- 爬标签：在startproject产生的spiders下只改label.py（输入输出都在里面做）

  scrapy crawl label

- 爬值：修改了item与pipeline，以规范化+实现去重与排列

  scrapy crawl countryspider

这样三个流程如流水线一般，就不需要手动参与，比如手动输入标签，引起乱码之类的后果。



**整个运行可通过bash a.sh来完成**

![a.sh](https://github.com/1012598167/my-tuchuang/raw/master/1560351889955.png)

并且爬标签时进行了去重和最常见40个标签排列，并直接写在pipeline内而不进行多余的txt/json文件处理。

## 代码

### 注释写得很全了，细节不多解释。

#### Talk is cheap, show me the code!!

#### country.py:



```python
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
```

注：通过爬去常见国家列表'https://www.worldometers.info/geography/alphabetical-list-of-countries/' 生成国家文件input.json, 注意json存的是字典！



修改的items.py

```python
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
```

注：这个item是一个字典！！！

![dict](https://github.com/1012598167/my-tuchuang/raw/master/1560352996453.png)

#### label.py:

```python
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
```

流程 一个request一个response，response完了给pipeline处理，pipeline return了再回来下一个request。

注：由于有些国家会有这样的情况

![mergedrow](https://github.com/1012598167/my-tuchuang/raw/master/1560352586598.png)

造成结果有一堆点之类不需要的结果

比如

![unexpected_output](https://github.com/1012598167/my-tuchuang/raw/master/1560267793956.png)

所以这里xpath有细改过。



#### pipeline.py:

```python
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
```

注：实时根据现有的标签排名更改输出 取前40个

![number_rank_of_label](https://github.com/1012598167/my-tuchuang/raw/master/1560352732272.png)

#### settings.py:

```python
# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'wiki_country.pipelines.WikiCountryPipeline': 300,
}
```

**一定要取消注释！不然pipeline没用！害了我很久！**

#### wiki.py:

```python
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
            #' ' 是一种奇怪的空格？？？？？？？？？？？？？？？/怎么办
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

```



## 中间版本

由于刚开始做的时候忘记传github了，所以中间很多写法都没了，亏死了555

这里仅存了一种非常复杂的写法，是我刚开始没有逻辑时的智障写法，可以引以为戒。

```python
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
        fields = response.css('.infobox').xpath('.//th[@scope="row"]')  # infobox中获取标签如Area Population
        #res = {}
        for field in fields:
            field=field.replace('\xa0', ' ')
            item=WikiCountryItem()
            key = field.xpath('.//text()').extract_first()  # 对应一个个标签比如Area
            if item not in self.items:
                self.items[key]=1
                #以此去重 若在字典里就不再加一遍
            else:
                self.items[key]+=1
            print('self.items:',self.items)
            item['label_num_dict']=sorted(self.items.keys())
            print("item['label_num_dict']",item['label_num_dict'])#把标签多的放在前面输出 这是一个列表！
            

```

#### 旧pipeline.py

```python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class WikiCountryPipeline(object):
    def __init__(self):
        self.filename = open(r'wiki_country/querys/fields.txt','w+', encoding='utf-8')#因为写的列表，所以覆盖写
    def process_item(self, item, spider):
        #if item['label']:
        #    self.filename.write(item['label']+',')
        #self.filename.close()
        #f2 = open(r'wiki_country/querys/fields.txt', 'w+', encoding='utf-8')#覆盖写
        for label_ in item['label_num_dict']:
            self.filename.write(label_ + ',')
        #field_set = self.filename.read().split(',')[:-1]#去掉最后一个逗号的空的

        return item
    def close_spider(self,spider):
        self.filename.close()
        #下面 吃掉最后一个逗号
        self.filename = open(r'wiki_country/querys/fields.txt', 'w+', encoding='utf-8')
        field_set = self.filename.read()[:-1]
        self.filename.write(field_set)
        self.filename.close()

```



## 实验效果

#### input.json

{"query":["Afghanistan","Albania","Algeria","Andorra","Angola","Antigua_and_Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan","Bolivia","Bosnia_and_Herzegovina","Botswana","Brazil","Brunei_","Bulgaria","Burkina_Faso","Burundi","Côte_d'Ivoire","Cabo_Verde","Cambodia","Cameroon","Canada","Central_African_Republic","Chad","Chile","China","Colombia","Comoros","Congo_(Congo-Brazzaville)","Costa_Rica","Croatia","Cuba","Cyprus","Czechia","Democratic_Republic_of_the_Congo","Denmark","Djibouti","Dominica","Dominican_Republic","Ecuador","Egypt","El_Salvador","Equatorial_Guinea","Eritrea","Estonia","Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Holy_See","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall_Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar_(formerly_Burma)","Namibia","Nauru","Nepal","Netherlands","New_Zealand","Nicaragua","Niger","Nigeria","North_Korea","North_Macedonia","Norway","Oman","Pakistan","Palau","Palestine_State","Panama","Papua_New_Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Rwanda","Saint_Kitts_and_Nevis","Saint_Lucia","Saint_Vincent_and_the_Grenadines","Samoa","San_Marino","Sao_Tome_and_Principe","Saudi_Arabia","Senegal","Serbia","Seychelles","Sierra_Leone","Singapore","Slovakia","Slovenia","Solomon_Islands","Somalia","South_Africa","South_Korea","South_Sudan","Spain","Sri_Lanka","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad_and_Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United_Arab_Emirates","United_Kingdom","United_States_of_America","Uruguay","Uzbekistan","Vanuatu","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"]}

#### fields.txt:

GDP,Capital,Government,Time zone,Currency,Driving side,Calling code,Internet TLD,Demonym(s),Legislature,ISO 3166 code,HDI,Official languages,Gini,Ethnic groups,Religion ,Date format,National language,Official language,Romanization,Spoken languages,IPA,Other languages,Official script,Hanyu Pinyin,Yale Romanization,National languages,Vernacular language,Official scripts,Vernacular,Inter-ethnic,Official language ,Simplified Chinese,Traditional Chinese,Bopomofo,Gwoyeu Romatzyh,Wade–Giles,Tongyong Pinyin,MPS2,Xiao'erjing,Pha̍k-fa-sṳ

#### results

![results](https://github.com/1012598167/my-tuchuang/raw/master/1560353464771-1560411815676.png)

![Afghansitan_output](https://github.com/1012598167/my-tuchuang/raw/master/1560353503631.png)

可以看到现在就没有乱码了

## 改版

*现在的github有两份文件，一份wiki_country，一份wiki_company*

wiki_country是主要文件 wiki_company:
这份company是基于country改的 只需要花一小时不到就能改成爬wiki的任何东西 但是:
爬的的确是company但是代码结构 文件地址 变量名称 注释 README都是country



所以若您对这份代码感兴趣，您可以先试着改成爬wiki的其他网站，再者爬任何静态网页。

## 致谢 

​	真的感谢王佳伟同学，我本来应该是爬公司的，他爬国家，做了五天才发现我做错了。。羞愧不已，王佳伟同学愿意在已经做完的情况下跟我换任务，给我腾出时间取赶其他ddl，感激不尽，好人一生平安！





