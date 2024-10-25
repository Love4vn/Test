import requests
import os
import urllib.request
from collections import defaultdict

# 检查目录是否存在,如果不存在则创建
if not os.path.exists('./IPTV/'):
    os.makedirs('./IPTV/')

# 文件 URL
url = "https://A.com/IPTV/main/IPTV.m3u"

# 下载 IPTV.m3u 文件
file_path = "./IPTV/IPTV.m3u"
urllib.request.urlretrieve(url, file_path)
print("m3u 文件下载完成")

# 发送请求获取文件内容
response = requests.get(url)
m3u_content = response.text

# 初始化字典
channels_dict = defaultdict(list)

# 提取频道信息
channels = []
group_title = ""
for i, line in enumerate(m3u_content.splitlines()):
    line = line.strip()
    if line.startswith("#EXTINF:"):
        # 从 #EXTINF: 行提取频道名称和分组信息
        channel_info = line.split(",")
        channel_name = channel_info[1].split(" ")[0] if len(channel_info) > 1 else ""  # 仅提取频道名称
        group_title = [item.split("group-title=")[1].split('"')[1] for item in channel_info if "group-title=" in item]
        group_title = group_title[0] if group_title else group_title
    elif line.startswith("http"):
        # 处理流媒体 URL 行
        streaming_url = line
        channels.append({"channel_name": channel_name, "group_title": group_title, "streaming_url": streaming_url, "line_index": i})

# 按照分组对频道进行分组
grouped_channels = defaultdict(list)
for channel in channels:
    grouped_channels[channel["group_title"]].append(channel)

# 按照行号对每个分组内部的频道进行排序
sorted_channels = []
for group_title, channels_in_group in grouped_channels.items():
    sorted_channels.extend(sorted(channels_in_group, key=lambda x: x["line_index"]))

# 输出到文件
output_file_path = "./IPTV/IPTV-tvbox.txt"
with open(output_file_path, "w", encoding="utf-8") as output_file:
    prev_group_title = None
    for channel in sorted_channels:
        group_title = channel["group_title"]
        channel_name = channel["channel_name"]
        streaming_url = channel["streaming_url"]
        if group_title != prev_group_title:
            if prev_group_title:
                output_file.write("\n")  # 在每个分组后添加一个空行
            if group_title:
                output_file.write(f"{group_title},#genre#\n")
            prev_group_title = group_title
        output_file.write(f"{channel_name},{streaming_url}\n")

print(f"提取完成,结果已保存到 {output_file_path}")
