import requests
import os
from datetime import datetime

# ================= 配置区域 =================
# 在这里填入你的直播源链接 (M3U 网址)
SOURCE_URLS = [
    "https://raw.githubusercontent.com/yeqi128/iptv/refs/heads/main/iptv.m3u",
    "https://epg.pw/test_channels_hong_kong.m3u",
    "https://epg.pw/test_channels_taiwan.m3u"
    # 在此处添加更多链接，保持格式不变
]

# 输出文件名 (后缀为 .txt)
OUTPUT_FILE = "merged_links.txt"
# ===========================================

def fetch_content(url):
    """下载文件内容"""
    try:
        print(f"正在下载: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return ""

def extract_links(contents):
    """从内容中提取 http/https 链接并去重"""
    unique_links = []
    seen_links = set()
    
    for content in contents:
        if not content:
            continue
        
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            # 只保留以 http 或 https 开头的行
            if line.startswith("http://") or line.startswith("https://"):
                if line not in seen_links:
                    unique_links.append(line)
                    seen_links.add(line)
            # 忽略所有 #EXTINF, #EXTM3U 等标签和频道名称
    
    return unique_links

def main():
    print("=== 开始合并直播源 ===")
    all_contents = []
    
    # 1. 下载所有源
    for url in SOURCE_URLS:
        content = fetch_content(url)
        if content:
            all_contents.append(content)
    
    if not all_contents:
        print("错误：没有成功下载任何内容！")
        return

    # 2. 提取并去重链接
    final_links = extract_links(all_contents)
    
    print(f"去重后共获得 {len(final_links)} 个有效链接。")

    # 3. 写入 TXT 文件
    # 可以在文件开头加一行注释说明更新时间（可选）
    output_content = f"# Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    output_content += "\n".join(final_links)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output_content)
    
    print(f"成功生成文件: {OUTPUT_FILE}")
    print(f"文件大小: {os.path.getsize(OUTPUT_FILE) / 1024:.2f} KB")

if __name__ == "__main__":
    main()
