import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import certifi

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器界面
# chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速

# 启动Chrome浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 创建保存TLE数据的目录
os.makedirs('tle_data', exist_ok=True)

# 读取已下载的链接
downloaded_links_file = 'downloaded_links.json'
if os.path.exists(downloaded_links_file):
    with open(downloaded_links_file, 'r') as file:
        downloaded_links = json.load(file)
else:
    downloaded_links = []

# 假设 satellite_links 列表已经填充了提取的链接
# satellite_links = [
#     "https://orbit.ing-now.com/satellite/25544/1998-067a/iss/",
#     "https://orbit.ing-now.com/satellite/48275/2021-035B/CZ-5B/",
#     # 其他链接...
# ]
satellite_links_file = 'satellite_links.json'

# 检查文件是否存在并读取内容
if os.path.exists(satellite_links_file):
    with open(satellite_links_file, 'r') as file:
        satellite_links = json.load(file)
else:
    satellite_links = []

# 打印读取的内容
print("satellite_links:", satellite_links)
# 过滤掉已下载的链接
satellite_links = [link for link in satellite_links if link not in downloaded_links]

for satellite_url in satellite_links:
    try:
        driver.get(satellite_url)
        print(f"Visiting {satellite_url}")

        # 等待页面加载完成
        time.sleep(5)

        # 查找“DOWNLOAD SATELLITE TLE DATA”链接
        download_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "DOWNLOAD SATELLITE TLE DATA"))
        )
        intermediate_url = download_link.get_attribute("href")
        driver.get(intermediate_url)
        print(f"Intermediate URL: {intermediate_url}")

        # 等待页面加载完成
        time.sleep(5)

        # 查找最终的“DOWNLOAD”链接
        final_download_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "DOWNLOAD"))
        )
        tle_url = final_download_link.get_attribute("href")
        print(f"Constructed TLE URL: {tle_url}")

        # 下载TLE数据
        tle_response = requests.get(tle_url, verify=certifi.where())
        tle_response.raise_for_status()

        # 提取文件名并保存TLE数据
        tle_filename = tle_url.split('/')[-2] + '.tle'
        with open(f"tle_data/{tle_filename}", 'wb') as file:
            file.write(tle_response.content)
        print(f"TLE data downloaded: {tle_filename}")

        # 将已下载的链接保存到文件中
        downloaded_links.append(satellite_url)
        with open(downloaded_links_file, 'w') as file:
            json.dump(downloaded_links, file)

    except Exception as e:
        print(f"Error occurred: {e}")

# 关闭浏览器
driver.quit()
