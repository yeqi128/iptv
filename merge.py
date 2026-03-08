import requests
import os
from datetime import datetime

# ================= 配置区域 =================
# 在这里填入你的直播源链接，每行一个
SOURCE_URLS = [
    "https://example.com/source1.m3u",
    "https://example.com/source2.m3u",
    "https://example.com/source3.m3u"
    # 添加更多源...
]

# 输出文件名
OUTPUT_FILE = "playlist.m3u"
# ===========================================

def fetch_m3u(url):
    """下载 m3u 内容"""
    try:
        print(f"正在下载: {url}")
        # 设置超时和伪装 Header，防止被某些站点拦截
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return ""

def parse_and_merge(contents):
    """解析并合并内容，进行简单去重"""
    merged_lines = []
    seen_channels = set() # 用于记录已存在的频道名称，防止重复
    
    # 写入 M3U 文件头
    merged_lines.append("#EXTM3U")
    merged_lines.append(f"# Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    current_info = None # 暂存 #EXTINF 行
    
    for content in contents:
        if not content.strip():
            continue
            
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#EXTM3U"):
                continue
            
            if line.startswith("#EXTINF"):
                current_info = line
                # 提取频道名称用于去重 (简单提取逗号后的名字)
                # 格式通常是 #EXTINF:-1 tvg-name="CCTV1",CCTV1
                # 这里简单取逗号后的部分作为唯一标识，可根据需要优化
                try:
                    channel_name = line.split(',')[-1].strip()
                except:
                    channel_name = line
            else:
                # 这是 URL 行
                if current_info:
                    # 如果这个频道名没出现过，或者你想保留所有源（注释掉 if 判断即可）
                    if channel_name not in seen_channels:
                        merged_lines.append(current_info)
                        merged_lines.append(line)
                        seen_channels.add(channel_name)
                    # 重置
                    current_info = None
    
    return "\n".join(merged_lines)

def main():
    print("开始合并直播源...")
    all_contents = []
    
    for url in SOURCE_URLS:
        content = fetch_m3u(url)
        if content:
            all_contents.append(content)
    
    if not all_contents:
        print("错误：没有成功下载任何源文件！")
        return

    final_content = parse_and_merge(all_contents)
    
    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"合并完成！共生成 {OUTPUT_FILE}")
    # 打印文件大小供参考
    size = os.path.getsize(OUTPUT_FILE)
    print(f"文件大小: {size / 1024:.2f} KB")

if __name__ == "__main__":
    main()
