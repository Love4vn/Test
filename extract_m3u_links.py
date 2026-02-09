#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M3U Stream Link Extractor for GitHub Actions
Tự động lấy link m3u/m3u8 từ trang web
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
from datetime import datetime
import os

class M3UStreamExtractor:
    def __init__(self, urls, output_dir='output'):
        self.urls = urls if isinstance(urls, list) else [urls]
        self.output_dir = output_dir
        self.all_links = []
        self.results = {}
        
        # Tạo thư mục output nếu chưa tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    def fetch_page(self, url):
        """Tải trang web"""
        try:
            print(f"📥 Đang tải: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            print(f"✅ Tải thành công!")
            return response.text
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def extract_m3u_links(self, html_content, base_url):
        """Trích xuất link m3u từ HTML"""
        links = set()
        
        # Phương pháp 1: Regex tìm link m3u8/m3u trực tiếp
        pattern = r'https?://[^"]*?\.m3u8?(?:\?[^"]*)?'
        found = re.findall(pattern, html_content)
        links.update(found)
        
        # Phương pháp 2: Tìm trong thẻ <a>
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            if 'm3u' in href.lower():
                full_url = urljoin(base_url, href)
                links.add(full_url)
        
        # Phương pháp 3: Tìm trong iframe
        for iframe in soup.find_all('iframe', src=True):
            src = iframe['src']
            if src and ('m3u' in src.lower() or 'stream' in src.lower()):
                full_url = urljoin(base_url, src)
                links.add(full_url)
        
        # Phương pháp 4: Tìm trong các script tags
        for script in soup.find_all('script'):
            if script.string:
                found = re.findall(pattern, script.string)
                links.update(found)
        
        return list(links)

    def extract_channel_info(self, html_content, base_url):
        """Trích xuất thông tin kênh phát sóng"""
        soup = BeautifulSoup(html_content, 'html.parser')
        channels = []
        
        # Tìm các link có liên quan đến stream/play
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            if any(kw in text.lower() or kw in href.lower() 
                   for kw in ['play', 'stream', 'watch', 'live', 'sports', 'tv']):
                channels.append({
                    'name': text[:100],
                    'url': urljoin(base_url, href),
                })
        
        return channels[:50]  # Giới hạn 50 kênh

    def process_url(self, url):
        """Xử lý một URL"""
        html = self.fetch_page(url)
        if not html:
            return None
        
        m3u_links = self.extract_m3u_links(html, url)
        channels = self.extract_channel_info(html, url)
        
        self.results[url] = {
            'timestamp': datetime.now().isoformat(),
            'total_links': len(m3u_links),
            'links': m3u_links,
            'channels': channels
        }
        
        self.all_links.extend(m3u_links)
        
        print(f"  📌 Tìm thấy {len(m3u_links)} link m3u")
        return m3u_links

    def save_m3u_playlist(self):
        """Lưu m3u playlist"""
        filename = os.path.join(self.output_dir, 'm3u_playlist.m3u')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            
            for idx, link in enumerate(self.all_links, 1):
                f.write(f'#EXTINF:-1,Stream {idx}\n')
                f.write(f'{link}\n')
        
        print(f"✅ Lưu playlist: {filename}")
        return filename

    def save_txt_list(self):
        """Lưu danh sách link dạng text"""
        filename = os.path.join(self.output_dir, 'm3u_links.txt')
        
        with open(filename, 'w', encoding='utf-8') as f:
            for link in self.all_links:
                f.write(f'{link}\n')
        
        print(f"✅ Lưu danh sách: {filename}")
        return filename

    def save_json_data(self):
        """Lưu dữ liệu JSON"""
        filename = os.path.join(self.output_dir, 'm3u_data.json')
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_urls': len(self.urls),
            'total_links': len(self.all_links),
            'details': self.results,
            'links': list(set(self.all_links))  # Loại bỏ duplicate
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Lưu JSON: {filename}")
        return filename

    def save_readme(self):
        """Tạo README"""
        filename = os.path.join(self.output_dir, 'README.md')
        
        content = f"""# M3U Stream Links

**Cập nhật lần cuối:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Thống kê
- **Tổng URL kiểm tra:** {len(self.urls)}
- **Tổng link tìm thấy:** {len(self.all_links)}

## Danh sách URL
"""
        for url in self.urls:
            links_count = self.results[url]['total_links'] if url in self.results else 0
            content += f"- {url} ({links_count} links)\n"
        
        content += f"\n## File output\n"
        content += f"- `m3u_playlist.m3u` - Playlist m3u format\n"
        content += f"- `m3u_links.txt` - Danh sách link (mỗi dòng một link)\n"
        content += f"- `m3u_data.json` - Dữ liệu JSON đầy đủ\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Tạo README: {filename}")

    def run(self):
        """Chạy extractor"""
        print("\n" + "="*60)
        print("🎬 M3U STREAM LINK EXTRACTOR")
        print("="*60)
        
        for url in self.urls:
            self.process_url(url)
        
        # Lưu kết quả
        self.save_m3u_playlist()
        self.save_txt_list()
        self.save_json_data()
        self.save_readme()
        
        print("\n" + "="*60)
        print(f"✅ Hoàn thành! Tìm thấy {len(self.all_links)} link")
        print("="*60 + "\n")


def main():
    # Danh sách URL cần extract
    urls = [
        'https://streamsports99.su/',
        # Thêm URL khác ở đây
    ]
    
    # Tạo extractor và chạy
    extractor = M3UStreamExtractor(urls, output_dir='output')
    extractor.run()


if __name__ == '__main__':
    main()