import base64
import random

import requests
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import cv2
import numpy as np
from selenium.webdriver.chrome.options import Options
headers1 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
    'Origin': 'https://accounts.douban.com',
    'Referer': 'https://accounts.douban.com/passport/login_popup?login_source=anony',
}
headers2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
}
login_list = [{'user': 'xxx', 'pas': 'xxx'}]
name = random.choice(login_list)
def shuru():
    # s1 = input('账号:')
    # s2 = input('密码:')
    s1 = name['user']
    s2 = name['pas']
    return s1, s2


def ocr(content):
    # https://www.douban.com/misc/captcha?id=QqteyXv9xuy60ZG6jd8VPlLt:en
    request_url = " https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    img = base64.b64encode(content)

    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=GaFltpbMuD2Ly9CsAAUcAAu1&client_secret=cg7jyi9rsQs0LIuzdb0tGyvy8afsq4hr'
    response = requests.get(host, timeout=5)
    if response:
        access_token = response.json()["access_token"]
    params = {"image": img}
    # access_token = '[调用鉴权接口获取的token]'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers, timeout=5)
    if response:
        return response.json()["words_result"][0]["words"]
def denglu(s1,s2):
    session = requests.session()
    url_login = 'https://accounts.douban.com/j/mobile/login/basic'
    data_login = {
        'ck': '',
        'remember': 'true',
        'name': s1,
        'password': s2,
    }
    print('******当前登录的账号为：{},密码：{}'.format(s1,s2))
    response1 = session.post(url_login, headers=headers1, data=data_login)
    print(response1.json()['description'])
    if response1.json()['description'] == '需要图形验证码':
        #231461887 231462356 231463947
        huadong()
        print('******豆瓣评论完成')
        exit(0)
def shibie(driver):
    image1 = driver.find_element_by_xpath('//*[@id="slideBg"]').get_attribute('src')
    image2 = driver.find_element_by_xpath('//*[@id="slideBlock"]').get_attribute('src')
    r1 = urllib.request.Request(image1)
    r1g = open('r1.png', 'wb+')
    r1g.write(urllib.request.urlopen(r1).read())
    r1g.close()
    r2 = urllib.request.Request(image2)
    r2g = open('r2.png', 'wb+')
    r2g.write(urllib.request.urlopen(r2).read())
    r2g.close()
    cv2.imwrite('r3.jpg', cv2.imread('r1.png', 0))
    cv2.imwrite('r4.jpg', cv2.imread('r2.png', 0))
    cv2.imwrite('r4.jpg', abs(255 - cv2.cvtColor(cv2.imread('r4.jpg'), cv2.COLOR_BGR2GRAY)))
    result = cv2.matchTemplate(cv2.imread('r4.jpg'), cv2.imread('r3.jpg'), cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)
    cv2.rectangle(cv2.imread('r3.jpg'), (y+20, x+20), (y + 136-25, x + 136-25), (7, 249, 151), 2)
    print('识别坐标为:', y+20)
    if y + 20 < 450: #如果缺口位置坐标小于450，刷新验证码重新计算缺口位置
        shuaxin = driver.find_element_by_xpath('//*[@id="reload"]/div')
        shuaxin.click()
        time.sleep(1)
        y = shibie(driver)
    return y
def huadong():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get('https://www.douban.com/')
    driver.implicitly_wait(10)
    iframe1 = driver.find_element_by_xpath('//*[@id="anony-reg-new"]/div/div[1]/iframe')
    driver.switch_to.frame(iframe1)  # 先进子页面iframe
    t1 = driver.find_element_by_xpath('/html/body/div[1]/div[1]/ul[1]/li[2]')
    t1.click()
    time.sleep(1)
    t2 = driver.find_element_by_xpath('//*[@id="username"]')
    t2.send_keys(s1)
    t3 = driver.find_element_by_xpath('//*[@id="password"]')
    t3.send_keys(s2)
    time.sleep(1)
    t4 = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/div[5]/a')
    t4.click()
    time.sleep(2)
    iframe2 = driver.find_element_by_id('tcaptcha_iframe')  # 定位到滑块验证码的iframe
    driver.switch_to.frame(iframe2)  # 切换到iframe
    xx = shibie(driver)
    x = int((xx - 70 + 20) / 2.41)  # 滑块的固定坐标为70，2.41是原图在网页上缩小为2.41倍
    tracks = [x + 30, -43, 8]
    huakuai = driver.find_element_by_id('tcaptcha_drag_thumb')
    ActionChains(driver).click_and_hold(on_element=huakuai).perform()
    for track in tracks:
        ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
    time.sleep(0.5)
    ActionChains(driver).release(on_element=huakuai).perform()
    time.sleep(2)
    print('*******登陆成功')
    # 231464271 231461887 231462356 231463947
    id_url = [ '235293143','235293706']
    for i in id_url:  # 第二个实例
        pinglun(i,driver)
def pinglun(i,driver):
    url = 'https://www.douban.com/group/topic/{}/'.format(i)
    driver.get(url)
    print('*******开始评论,当前评论url为:{}'.format(url))
    driver.execute_script("arguments[0].click()",driver.find_element_by_xpath("//textarea[@id='last']"))
    driver.find_element_by_xpath("//textarea[@id='last']").clear()
    driver.find_element_by_xpath("//textarea[@id='last']").send_keys("没剩几天了 加油")
    # 判断有没有验证码
    try:
        url = driver.find_element_by_xpath('//*[@id="captcha_image"]').get_attribute('src')
        if url:
            r = requests.get(url, headers=headers2, )
            with open('ocr.jpg', 'wb') as file:
                file.write(r.content)
            corcode = ocr(r.content)
            time.sleep(5)
            print('*****验证码识别成功，当前验证码链接:{},验证码:{}'.format(url, corcode))
            driver.find_element_by_xpath("//input[@id='captcha_field']").click()
            driver.find_element_by_xpath("//input[@id='captcha_field']").clear()
            driver.find_element_by_xpath("//input[@id='captcha_field']").send_keys("{}".format(corcode))
            time.sleep(5)
            driver.find_element_by_name("submit_btn").click()
            try:
                text_el = driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div[4]/form/div[2]').text
                if text_el:
                    print('*******评论失败,{}'.format(text_el))
                    pinglun(i, driver)
                else:
                    time.sleep(5)
                    print('****评论成功',)
            except:
                print('*******评论成功')
    except:
        print('*******没有验证码直接评论成功')
        driver.find_element_by_name("submit_btn").click()

s1,s2 = shuru()
denglu(s1, s2)
