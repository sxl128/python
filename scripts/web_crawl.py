
from selenium import webdriver #selenium 版本4.80
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from time import sleep
import urllib
import random
import re
import cv2
import threading


# 封装的计算图片距离的算法
def get_pos(imageSrc):
    # 读取图像文件并返回一个image数组表示的图像对象
    image = cv2.imread(imageSrc)
    # GaussianBlur方法进行图像模糊化/降噪操作。
    # 它基于高斯函数（也称为正态分布）创建一个卷积核（或称为滤波器），该卷积核应用于图像上的每个像素点。
    blurred = cv2.GaussianBlur(image, (5, 5), 0, 0)
    # Canny方法进行图像边缘检测
    # image: 输入的单通道灰度图像。
    # threshold1: 第一个阈值，用于边缘链接。一般设置为较小的值。
    # threshold2: 第二个阈值，用于边缘链接和强边缘的筛选。一般设置为较大的值
    canny = cv2.Canny(blurred, 0, 100)  # 轮廓
    # findContours方法用于检测图像中的轮廓,并返回一个包含所有检测到轮廓的列表。
    # contours(可选): 输出的轮廓列表。每个轮廓都表示为一个点集。
    # hierarchy(可选): 输出的轮廓层次结构信息。它描述了轮廓之间的关系，例如父子关系等。
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 遍历检测到的所有轮廓的列表
    for contour in contours:
        # contourArea方法用于计算轮廓的面积
        area = cv2.contourArea(contour)
        # arcLength方法用于计算轮廓的周长或弧长
        length = cv2.arcLength(contour, True)
        # 如果检测区域面积在5025-7225之间，周长在300-380之间，则是目标区域
        if 5025 < area < 7225 and 300 < length < 380:
            # 计算轮廓的边界矩形，得到坐标和宽高
            # x, y: 边界矩形左上角点的坐标。
            # w, h: 边界矩形的宽度和高度。
            x, y, w, h = cv2.boundingRect(contour)
            print("计算出目标区域的坐标及宽高：", x, y, w, h)
            # 在目标区域上画一个红框看看效果
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.imwrite("111.jpg", image)
            return x
    return 0

def recursiveClickDirs(ele):
        dirs = ele.find_elements(By.XPATH, 'following-sibling::*//*[@class="fish-collapse-header"]')
        if len(dirs) == 0:
            ele.click()
            # dirs = ele.find_elements(By.XPATH, './/*[@class="fish-collapse-header"]')
            dirs = ele.find_elements(By.XPATH, 'following-sibling::*//*[@class="fish-collapse-header"]')
        sleep(1)
        print("文件夹名称：{0}, 子文件夹数量：{1}".format(ele.text, len(dirs)))
        for dire in dirs:
            print('inner==' + dire.text)
            try: 
                dire.click()
                dire.click()
            except ElementNotInteractableException:
                ele.click()
            recursiveClickDirs(dire)
    

# 定义一个函数来定时检查元素
def check_element():
    interval = 1  # 每次检查间隔 1 s
    element_found = False

    while True:
        try:
            # 尝试查找元素
           
            # element = driver.find_element(By.XPATH, '//button[@class="fish-btn fish-btn-primary"]')
            element = driver.find_element(By.XPATH, '//*[@id="zxxcontent"]/div[4]/div/div/micro-app/micro-app-body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/button')
            if not element_found:
                print("元素已出现！")
                sleep(1)
                element.click()
                element_found = True
            
        except NoSuchElementException:
            print("元素未出现，等待中...")
            sleep(interval)
    # 可以选择关闭浏览器，视需求而定
    # driver.quit()    

def recursive_get_parent(ele):
    try:
        dire = ele.find_element(By.XPATH, 'ancestor::*[@class="fish-collapse-item"][1]')
        print(dire.get_attribute('outerHTML'))
        recursive_get_parent(dire)
    except NoSuchElementException:
        print(ele.get_attribute('outerHTML'))
        ele.click()
        pass

#浏览器驱动初始化
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
# options.add_argument("--auto-open-devtools-for-tabs")
driver = webdriver.Chrome(options=options)
 
#网页最大化
driver.maximize_window()
 
#打开国家中小学智慧教育平台首页
driver.get('https://www.smartedu.cn')
sleep(5)
 
#点击登录按钮，进入登录页面
driver.find_element(By.XPATH,'//*[@class="index-module_register_btn_xw8bx theme-register-btn"]').click()
sleep(5)

#填写手机号和密码，打勾，点击登录
driver.find_element(By.ID,'username').send_keys('18222576598')
driver.find_element(By.ID,'tmpPassword').send_keys('Ragzrash135.')
driver.find_element(By.ID,'agreementCheckbox').click()
driver.execute_script("window.sliderFlag = true;")
driver.find_element(By.ID,'loginBtn').click()
sleep(5)
 
# 此时需要切换到弹出的滑块区域，需要切换frame窗口
driver.switch_to.frame("tcaptcha_iframe_dy")
# 找到滑块
# 等待滑块验证图片加载后，再做后面的操作
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'slideBg')))


# 获取滑块验证图片下载路径，并下载到本地
bigImage = driver.find_element(By.ID, "slideBg")
s = bigImage.get_attribute("style")  # 获取图片的style属性
# 设置能匹配出图片路径的正则表达式
p = r'background-image: url\(\"(.*?)\"\);'
# 进行正则表达式匹配，找出匹配的字符串并截取出来
bigImageSrc = re.findall(p, s, re.S)[0]  # re.S表示点号匹配任意字符，包括换行符
print("滑块验证图片下载路径:", bigImageSrc)
# 下载图片至本地
urllib.request.urlretrieve(bigImageSrc, 'bigImage.png')

# 计算缺口图像的x轴位置
dis = get_pos('bigImage.png')
# 整体等待5秒看结果
sleep(5)

# 获取小滑块元素，并移动它到上面的位置
smallImage = driver.find_element(By.XPATH, '//*[@id="tcOperation"]/div[6]')
# 小滑块到目标区域的移动距离（缺口坐标的水平位置距离小滑块的水平坐标相减的差）
# 新缺口坐标=原缺口坐标*新画布宽度/原画布宽度
newDis = int(dis*280/672-smallImage.location['x'])

driver.implicitly_wait(5)  # 使用浏览器隐式等待5秒
# 按下小滑块按钮不动
ActionChains(driver).click_and_hold(smallImage).perform()
# 移动小滑块，模拟人的操作，一次次移动一点点
i = 0
moved = 0
while moved < newDis:
    x = random.randint(3, 10)  # 每次移动3到10像素
    moved += x
    ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    print("第{}次移动后，位置为{}".format(i, smallImage.location['x']))
    i += 1
# 移动完之后，松开鼠标
ActionChains(driver).release().perform()
# 整体等待5秒看结果
sleep(5)


# 登录成功之后打开暑期研修界面
driver.get('https://www.smartedu.cn/special/TeacherTraining2024')
# 等待5s观察效果
sleep(5)

# 浏览器句柄 0 - 视频选择页，1 - 视频播放页
window_handles = []
window_handles.append(driver.current_window_handle)
 # 切换到选择的 iframe
iframe = driver.find_elements(By.TAG_NAME,'iframe')[0]
driver.switch_to.frame(iframe)
WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="fish-tabs-tab-btn"]')))
tabs = driver.find_elements(By.XPATH, '//*[@class="fish-tabs-tab-btn"]')

tab_length = len(tabs)
print("tab 数量: {0}".format(tab_length))


# 创建一个线程来运行检查函数
check_thread = threading.Thread(target=check_element)
# 启动线程
check_thread.start()
for i in range(tab_length):
    tab = driver.find_elements(By.XPATH, '//*[@class="fish-tabs-tab-btn"]')[i]
    tab.click()
    sleep(3)
    # elements = driver.find_elements(By.XPATH, '//*[@class="index-module_chapter_H3nnL"]')
    elements = driver.find_elements(By.XPATH, '//*[@class="index-module_box_eNttn index-module_common_box_KJzbE"]')
    video_counts = len(elements)
    print("当前页面视频数量: {0}".format(video_counts))
    for j in range(video_counts):
        element = driver.find_elements(By.XPATH, '//*[@class="index-module_box_eNttn index-module_common_box_KJzbE"]')[j].find_element(By.XPATH, '(.//*[@class="index-module_chapter_H3nnL"])[1]')
        element.click()
        # 等待 5s
        sleep(5)
        print(driver.current_url)

         # 循环执行，直到找到一个新的窗口句柄
        for window_handle in driver.window_handles:
            print('cur == ' + driver.current_url)
            if window_handle != window_handles[0]:
                driver.switch_to.window(window_handle)
                print('next == ' + driver.current_url)
                window_handles.append(window_handle)
                break
        print(driver.current_url)
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="main"]/div/div/div/div/section/div/div/div[3]/div/div[2]/span')))
            # 检查当前视频是否已经学习完成
            progress = driver.find_element(By.XPATH,'//*[@id="main"]/div/div/div/div/section/div/div/div[3]/div/div[2]/span')
            if "100" in progress.text:
                #关闭标签页或窗口
                driver.close()
                #切回到之前的标签页或窗口
                driver.switch_to.window(window_handles[0])
                # 切换到选择的 iframe
                iframe = driver.find_elements(By.TAG_NAME,'iframe')[0]
                driver.switch_to.frame(iframe)
                continue
        except Exception as e:
            pass

        # 找到页面上的第一个视频
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '(//*[@class="resource-item resource-item-train "])[1]')))
        inner_content = driver.find_element(By.XPATH, '(//*[@class="resource-item resource-item-train "])[1]')

        inner_content.click()
        sleep(16)
        try: 
            ele = driver.find_element(By.XPATH, '//*[@id="zxxcontent"]/div[4]/div/div/micro-app/micro-app-body/div[2]/div/div[2]/div/div[2]/div[2]/div/div[2]/div[2]/div[2]')
            ele.click()
        except NoSuchElementException:
            pass
        sleep(5)
        # 点击页面上所有可点击的折叠文件夹，加载所有视频
        dirs = driver.find_elements(By.XPATH, '//*[@class="fish-collapse-header"]')
        print(len(dirs))
        for dire in dirs:
            recursiveClickDirs(dire)
        # 找到页面上第一个未学完/进行中的视频
        videos = driver.find_elements(By.XPATH, '//i[@title="未开始" or @title="进行中"]')
        for video in videos:
            # 使用 XPath 获取父元素
            try:
                # dire = video.find_element(By.XPATH, 'ancestor::*[@class="fish-collapse-item"][1]')
                # recursive_get_parent(dire)
                # 查找所有符合条件的祖先节点
                dires = video.find_elements(By.XPATH, 'ancestor::*[@class="fish-collapse-item"]')
                print("祖先节点数量为 {0}".format(len(dires)))
                for dire in dires:
                    print("节点 class 属性为：{0}".format(dire.get_attribute("class")))
                    dire.click()
            except NoSuchElementException:
                pass
            sleep(2)
            video.click()
            sleep(2)
            driver.find_element(By.XPATH, '//button[@title="播放视频"]').click()
            sleep(5)

            try:
                element = driver.find_element(By.XPATH, '//*[@id="zxxcontent"]/div[4]/div/div/micro-app/micro-app-body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/button')
                element.click()
            except NoSuchElementException:
                pass
            sleep(5)
            # 设置速度
            double_speed = True
            try:
                rate = driver.find_element(By.XPATH, '//button[@title="播放速度"]')
                ActionChains(driver).move_to_element(rate).perform()
                # 点击倍速
                driver.find_element(By.XPATH, '(//li[@role="menuitemradio"])[1]').click()
            except Exception as e:
                double_speed = False
                pass
            duration_text = driver.find_element(By.XPATH, '//span[@class="vjs-duration-display"]').text
            duration_array = duration_text.split(":")
            if len(duration_array) == 2:
                duration = int(duration_array[0]) * 60 + int(duration_array[1])
                print(duration)
            else:
                duration = int(duration_array[0]) * 3600 + int(duration_array[1]) * 60 + int(duration_array[2])

            currnet_text = driver.find_element(By.XPATH, '//span[@class="vjs-current-time-display"]').text
            print('==' + currnet_text)
            current_array = currnet_text.split(":")
            if len(current_array) != 0:
                if len(current_array) == 2:
                    current = int(current_array[0]) * 60 + int(current_array[1])
                    remain = duration - current
                else:
                    current = int(current_array[0]) * 3600 + int(current_array[1]) * 60 + int(current_array[2])
                    remain = duration - current
                print(remain)
                if double_speed:
                    sleep((remain) / 2 + 7)
                else:
                    sleep(remain + 7)
            else:
                if double_speed:
                    sleep(duration / 2 + 7)
                else:
                    sleep(duration + 7)
            
         #关闭标签页或窗口
        driver.close()
        #切回到之前的标签页或窗口
        driver.switch_to.window(window_handles[0])
         # 切换到选择的 iframe
        iframe = driver.find_elements(By.TAG_NAME,'iframe')[0]
        driver.switch_to.frame(iframe)

        
            

    


# #安全退出
# #点击个人图标
# driver.find_element(By.XPATH,'//*[@id="header"]/div/div[2]/div[2]/div[2]/div[2]/div/div/a/div').click()
# sleep(3)
# #点击安全退出
# driver.find_element(By.CLASS_NAME,'index-module_panel-logout_bpb5u').click()