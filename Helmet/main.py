from bs4 import BeautifulSoup
import os
import urllib
import time
def SaveImage(link,word,count):
    try:
        time.sleep(0.2)
        urllib.request.urlretrieve(link,'./'+word + '/'+str(count) + '.jpg')
    except:
        time.sleep(1)
        print("error")
    else:
        print("已经有了" + str(count) + "张图")

def FindLink(PageNum, InputData, word):
    for i in range(PageNum):
        print(i)
        try:
            url = 'http://cn.bing.com/images/async?q={0}&first={1}&count=35&relp=35&lostate=r&mmasync=1&dgState=x*175_y*848_h*199_c*1_i*106_r*0'
            # 定义请求头
            agent = {
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.165063 Safari/537.36 AppEngine-Google."}
            page1 = urllib.request.Request(url.format(InputData, i * 35 + 1), headers=agent)
            page = urllib.request.urlopen(page1)
            soup = BeautifulSoup(page.read(), 'html.parser')
            # 创建文件夹
            if not os.path.exists("./" + word):
                os.mkdir('./' + word)

            for StepOne in soup.select('.mimg'):
                link = StepOne.attrs['src']
                count = len(os.listdir('./' + word)) + 1
                SaveImage(link, word, count)
        except:
            print('URL OPENING ERROR !')
if __name__ == "__main__":
    pagenum =100
    word = '头盔'
    input_data = urllib.parse.quote(word)
    FindLink(pagenum,input_data,word)
