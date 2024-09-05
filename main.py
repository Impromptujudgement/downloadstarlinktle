import asyncio
import json
import os

import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器界面
# chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速

# 启动Chrome浏览器
service = Service('../chromedriver-win64/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# 创建保存TLE数据的目录
os.makedirs('tle_data', exist_ok=True)

# 读取已下载的链接
downloaded_links_file = 'downloaded_links.json'
if os.path.exists(downloaded_links_file):
    with open(downloaded_links_file, 'r') as file:
        downloaded_links = json.load(file)
else:
    downloaded_links = []

# 读取卫星链接
satellite_links_file = 'satellite_links.json'
if os.path.exists(satellite_links_file):
    with open(satellite_links_file, 'r') as file:
        satellite_links = json.load(file)
else:
    satellite_links = []

omit_links_file = 'omiturl.json'
if os.path.exists(omit_links_file):
    with open(omit_links_file, 'r') as file:
        omit_links = json.load(file)
else:
    omit_links = []
# 打印读取的内容
# print("satellite_links:", satellite_links)

# 过滤掉已下载的链接
satellite_links = [link for link in satellite_links if link not in downloaded_links]


async def download_tle(session, tle_url):
    try:
        async with session.get(tle_url, verify_ssl=False) as response:
            response.raise_for_status()
            tle_filename = tle_url.split('/')[-2] + '.tle'
            with open(f"tle_data/{tle_filename}", 'wb') as tlefile:
                tlefile.write(await response.read())
            print(f"TLE data downloaded: {tle_filename}")
    except Exception as e:
        print(f"Error occurred: {e}")


async def main():
    tle_urls = []
    # for satellite_url in satellite_links:
    for satellite_url in omit_links:
        try:
            driver.get(satellite_url)
            print(f"Visiting {satellite_url}")

            # 等待页面加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )

            # 查找“DOWNLOAD SATELLITE TLE DATA”链接
            download_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "DOWNLOAD SATELLITE TLE DATA"))
            )
            intermediate_url = download_link.get_attribute("href")
            driver.get(intermediate_url)
            print(f"Intermediate URL: {intermediate_url}")

            # 等待页面加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )

            # 查找最终的“DOWNLOAD”链接
            final_download_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "DOWNLOAD"))
            )
            tle_url = final_download_link.get_attribute("href")
            print(f"Constructed TLE URL: {tle_url}")

            tle_urls.append(tle_url)

        except Exception as e:
            print(f"Error occurred: {e}")

    async with aiohttp.ClientSession() as session:
        tasks = [download_tle(session, tle_url) for tle_url in tle_urls]
        await asyncio.gather(*tasks)

    # 将已下载的链接保存到文件中
    downloaded_links.extend(satellite_links)
    with open(downloaded_links_file, 'w') as file:
        json.dump(downloaded_links, file)

    driver.quit()


if __name__ == "__main__":
    asyncio.run(main())
