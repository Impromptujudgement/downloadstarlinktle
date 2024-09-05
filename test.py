import certifi
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import json

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器界面
chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速

# 启动Chrome浏览器
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 主页面URL
base_url = "https://orbit.ing-now.com/starlink/"

# 访问主页面
driver.get(base_url)

# 等待页面加载完成
time.sleep(5)  # 等待5秒，确保数据加载完成

# 查找并打印表格中的所有链接
satellite_links = []


def extract_links_from_page():
    # 打印当前页面的URL
    print(f"Current page URL: {driver.current_url}")

    table = driver.find_element(By.ID, "objectstable")  # 假设表格有一个ID为"objectstable"
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        try:
            # 打印表格行的HTML内容
            print("Row HTML:")
            print(row.get_attribute('innerHTML'))

            # 查找<a>标签
            a_tags = row.find_elements(By.TAG_NAME, "a")
            if a_tags:
                for a_tag in a_tags:
                    href = a_tag.get_attribute("href")
                    if href and href.startswith("https://orbit.ing-now.com/satellite/"):
                        satellite_links.append(href)
            else:
                print("No <a> tag found in this row.")
        except Exception as e:
            print(f"Error occurred: {e}")


# 提取第一页的链接
extract_links_from_page()

# 查找分页按钮并遍历所有页面
while True:
    try:
        # 查找下一页按钮
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "objectstablehtml_next"))
        )
        if "disabled" in next_button.get_attribute("class"):
            break  # 如果按钮被禁用，说明已经到达最后一页

        # 使用 JavaScript 点击按钮
        driver.execute_script("arguments[0].click();", next_button)

        # 等待页面加载完成
        time.sleep(5)

        # 提取当前页的链接
        extract_links_from_page()
    except Exception as e:
        print(f"Error occurred: {e}")
        break

# 打印所有提取的链接
print("Extracted satellite links:")
for link in satellite_links:
    print(link)

# 假设 satellite_links 列表已经填充了提取的链接

# 保存到本地文件
with open('satellite_links.json', 'w') as file:
    json.dump(satellite_links, file)

print("Satellite links saved to satellite_links.json")

# 创建保存TLE数据的目录
os.makedirs('tle_data', exist_ok=True)

# 访问每个卫星页面并下载TLE数据
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
    except Exception as e:
        print(f"Error occurred: {e}")

# 关闭浏览器
driver.quit()
