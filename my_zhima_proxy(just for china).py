import requests
def get_ip_list():
    print("正在获取代理列表...")
    url="http://http.tiqu.alicdns.com/getip3?num=1&type=3&pro=&city=0&yys=0&port=1&pack=59825&ts=0&ys=0&cs=0&lb=2&sb=0&pb=4&mr=1&regions=&gm=4" #从代理网站上获取的url
    page = requests.get(url)
    iplist = page.text
    ip_list = iplist.split('</br>')
    print(len(ip_list)-1)
    if len(ip_list)==1:
        print("ip获取失败")
    print("代理列表抓取成功……")
    return ip_list[:-1]

#格式化ip，获取一个proxise
def get_proxies(ip):
    proxy_ip = 'http://' + ip
    proxies = {'http': proxy_ip}
    return proxies

#getHTMLText(url,proxies)这是一个通用的爬虫框架应该不陌生
def getHTMLText(url,proxies):    
    try:
        r = requests.get(url,proxies=proxies)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
    except (requests.exceptions.ConnectionError,ConnectionError):
        return 0
    except:
        return 0
    else:
        return r.text

def main():
    #找到访问网站的url构造规律，构造url
    start_url = ''
    ur=''       
    iplist = get_ip_list()
    i = 1     #标记当前爬取页面
    page=1000 
    #page值可以用用类似原理按需获取，这里假设爬取某个网站的1000页数据
    while i<= page:
        iplist = get_ip_list()
        if len(iplist) == 0:
            j = 1
            while len(iplist) == 0 and j < 10:
                print("没有可用ip，休眠2秒")
                time.sleep(2)
                iplist = get_ip_list()
                j += 1
            if len(iplist) == 0:
                print("多次访问依然没有ip，放弃……")
                break
        for ip in iplist:
            while i <= page:
                print("页码")
                print(i)         #用于检验爬取页码进度
                url = start_url + ur + str(i) #构造的待访问网站url
                proxies = get_proxies(ip)
                html = getHTMLText(url, proxies)
                if html == 0:
                    break
                else:
                    content=get_info(html) #get_info内容解析函数，按照需要自己写吧
                    i+=1
            if i>page:
                break 
