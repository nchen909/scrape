# 阿布云IP代理池配置
# ipNumber = 0
# def getProxy():
#     global ipNumber
#     ipNumber = ipNumber + 1
#     print("当前为第"+str(ipNumber)+"ip")
#     # 代理服务器
#     proxy_host = 'http-dyn.abuyun.com'
#     proxy_port = '9020'
#
#     # 代理隧道验证信息
#     proxy_user = 'HLXY02NA184KY87D'
#     proxy_pass = '645C093E0723D7F1'
#
#     proxy_meta = 'http://%(user)s:%(pass)s@%(host)s:%(port)s' % {
#         'host': proxy_host,
#         'port': proxy_port,
#         'user': proxy_user,
#         'pass': proxy_pass,
#     }
#     proxies = {
#         'http': proxy_meta,
#         'https': proxy_meta,
#     }
#     return proxies

# 芝麻http代理池配置
import requests

proxyHost = "122.246.97.0"
proxyPort = "4286"
ipNumber = 0


# 请求芝麻http更新代理ip
def updateProxy():
    global proxyHost, proxyPort, ipNumber
    url = "http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&pack=37176&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions="
    res = requests.get(url).text
    proxyHost = res.split(":")[0]
    proxyPort = res.split(":")[1][:-2]  # 去掉末尾\r\n

    print(str(proxyHost), end='')
    print(str(proxyPort), end='')
    ipNumber = ipNumber + 1
    print("当前第"+str(ipNumber)+"IP,已更新代理IP:"+res)


updateProxy()


def getProxy():
    global proxyHost, proxyPort
    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    # print("当前代理===="+str(proxyHost)+":"+str(proxyPort))
    return proxies


def getIP():
    return proxyHost + ":" + proxyPort
