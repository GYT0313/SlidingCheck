from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from io import BytesIO
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import random
"""
使用极验滑动验证码的官网实验，若没有账号需要先注册
"""
EMAIL = '873560792@qq.com'
PASSWORD = '密码'

class CrackGeetest():
    """[summary]
    
    初始化
    """
    def __init__(self):
        self.url = 'https://account.geetest.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 5)
        self.email = EMAIL
        self.password = PASSWORD

    def __del__(self):
        self.browser.close()

    def get_geetest_button(self):
        """[summary]
        
        获取初始验证按钮
        返回按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        return button

    def get_position(self):
        """[summary]
        
        获取验证码位置
        返回验证码位置元组
        """
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """[summary]
        
        获取网页截图
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_geetest_image(self, name='captcha.png'):
        """[summary]
        
        获取验证码图片
        返回图片对象
        """
        top, bottom, left, right = self.get_position()
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_slider(self):
        """[summary]
        
        获取滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider


    def open(self):
        """[summary]
        
        输入用户及密码
        """
        self.browser.get(self.url)
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'email')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        email.send_keys(self.email)
        password.send_keys(self.password)


    def get_track(self, distance):
        """[summary]
        
        根据偏移量获取移动轨迹
        
        Arguments:
            distance {[type]} -- 偏移量
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阀值
        mid = distance * 7/10
        # 计算间隔
        t = 0.15
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正
                a = 2.1
            else:
                # 加速度为负 
                a = -4.8
            # 初速度v0
            v0 = v
            # 当前速度 v = v0 + at
            v = v0 + a*t
            # 移动距离 x = v0t + 1/2*a*t*t
            move = v0*t + 1/2*a*t*t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move, 2))
        return track

    def move_to_gap(self, slider, tracks):
        """[summary]
        
        拖动滑块到缺口处
        
        Arguments:
            slider {[type]} -- 滑块
            tracks {[type]} -- 轨迹
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in tracks:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.1)
        ActionChains(self.browser).release().perform()


    def login(self):
        """[summary]
        
        登录
        """
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login-btn')))
        submit.click()
        time.sleep(1)
        print('登录成功')


    def is_try_again(self):
        """[summary]
        
        判断是否能够点击重试
        """
        button_text = self.browser.find_element_by_class_name('geetest_radar_tip_content')
        text = button_text.text
        if text == '尝试过多':
            button = self.browser.find_element_by_class_name('geetest_reset_tip_content')
            button.click()

    def is_success(self):
        """[summary]
        
        判断是否成功
        """
        button_text2 = self.browser.find_element_by_class_name('geetest_success_radar_tip_content')
        text2 = button_text2.text
        if text2 == '验证成功':
            return 1
        return 0

    def for_move(self, x_temp):
        """[summary]
        
        循环拖动
        """
        flag = 0
        for i in range(0,7):
            
            gap = random.randint(16, 20)*i + x_temp
            if gap < 40:
                continue
            print('预估计缺口位置: ', gap)
            self.is_try_again()
            slider = self.get_slider()
            track = self.get_track(gap)
            print('滑动轨迹: ', track)
            # 拖动滑块
            self.move_to_gap(slider, track)
            time.sleep(3)
            if self.is_success():
                flag = 1
                break
        return flag

    def crack(self):
        """[summary]
        
        验证
        """
        try:
            # 输入用户和密码
            self.open()
            # 点击验证按钮
            button = self.get_geetest_button()
            button.click()
            # 获取验证码图片
            image1 = self.get_geetest_image('captcha1.png')
            flag = 0
            while 1:
                temp = random.randint(0, 2) # 将轨迹划分为2, 则有1/2的几率
                if temp == 0:
                    print('预估左1/2: ')
                    flag = self.for_move(30)
                else:
                    print('预估右1/2: ')
                    flag = self.for_move(120)
                if flag == 1:
                    break
            
        except TimeoutException as e:
            self.crack()
        # 成功,登录
        self.login()
        time.sleep(10)


if __name__ == "__main__":
    crack = CrackGeetest()
    crack.crack()
