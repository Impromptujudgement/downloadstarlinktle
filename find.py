import os
import json

# 定义 JSON 文件路径
json_file_path = './satellite_links.json'

# 定义文件夹路径
folder_path = './tle_data'
omit_links_file = 'omiturl.json'
if os.path.exists(omit_links_file):
    with open(omit_links_file, 'r') as file:
        omit_links = json.load(file)
else:
    omit_links = []
# 读取 JSON 文件并提取 URL 列表
with open(json_file_path, 'r') as json_file:
    urls = json.load(json_file)

# 初始化缺失文件列表

# 遍历 URL 列表
for url in urls:
    # 提取 URL 中的文件名部分（例如：2024-150n）
    file_name = url.split('/')[-3]

    # 构建 TLE 文件名（例如：2024-150N.tle）
    tle_file_name = f"{file_name.upper()}.tle"
    # print(tle_file_name)

    # 检查文件是否存在
    if not os.path.isfile(os.path.join(folder_path, tle_file_name)):
        # 如果文件不存在，则将 URL 添加到缺失文件列表中
        if url not in omit_links:  # 避免重复添加
            omit_links.append(url)
with open(omit_links_file, 'w') as file:
    json.dump(omit_links, file)
# 显示缺失文件对应的网址
print('Missing TLE Files:')
for missing_url in omit_links:
    print(missing_url)
