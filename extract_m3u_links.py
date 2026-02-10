#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stream Extractor using Selenium + webdriver-manager
"""

import os
import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin

def install_dependencies():
    """Cài đặt dependencies"""
    try:
        import selenium
        import beautifulsoup4
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("⚠️ Cài đặt dependencies...")
        os.system('pip install selenium beautifulsoup4 webdriver-manager')

install_dependencies()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class StreamExtractorSelenium:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        self.all_streams = []
        os.makedirs(output_dir, exist_ok=True)

    def init_driver(self):
        """Khởi tạo Selenium WebDriver"""
        print("🔧 Khởi tạo Chrome driver...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Sử dụng webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Chrome driver ready")
            return driver
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def get_page_source(self, url, driver):
        """Tải trang với Selenium"""
        try:
            print(f"  📥 {url}")
            driver.get(url)
            
            # Chờ body load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            print(f"  ✅ OK")
            return driver.page_source
        except Exception as e:
            print(f"  ❌ {e}")
            return None

    def extract_player_links(self, html, base_url):
        """Trích xuất link từ trang chủ"""
        links = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Tìm tất cả link chứa /player/
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                
                if '/player/' in href:
                    full_url = urljoin(base_url, href)
                    links.append({
                        'name': text or 'Unknown',
                        'url': full_url
                    })
            
            print(f"  ✓ Tìm {len(links)} player links")
            
        except Exception as e:
            print(f"  ⚠️ {e}")
        
        return links

    def extract_stream_url(self, html):
        """Trích xuất stream URL từ player HTML"""
        links = set()
        
        try:
            # Regex patterns
            patterns = [
                r'"?(?:src|url|source)"?\s*:\s*"([^"]*\.(?:m3u8|mpd|mp4|ts)[^"]*)"',
                r'(?:src|data-src)=["\'](https?://[^\'"]*\.(?:m3u8|mpd|ts|mp4)[^\'"]*)["\']',
                r'https?://[^\s"\'<>]*?\.(?:m3u8|mpd|ts|mp4)(?:[?#][^\s"\'<>]*)?',
            ]
            
            for pattern in patterns:
                found = re.findall(pattern, html, re.IGNORECASE)
                links.update(found)
            
            # Tìm trong script
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup.find_all('script'):
                if script.string:
                    found = re.findall(
                        r'https?://[^\s"\'<>]*?\.(?:m3u8|mpd|ts|mp4)',
                        script.string,
                        re.IGNORECASE
                    )
                    links.update(found)
            
            return list(links)
            
        except Exception as e:
            print(f"  ⚠️ {e}")
            return []

    def process_streams(self, base_url):
        """Xử lý streams"""
        driver = self.init_driver()
        
        if not driver:
            print("❌ Không thể khởi tạo driver")
            return
        
        try:
            print(f"\n🔍 Quét: {base_url}\n")
            
            # Tải trang chủ
            html = self.get_page_source(base_url, driver)
            
            if not html:
                return
            
            # Tìm player links
            player_links = self.extract_player_links(html, base_url)
            
            if not player_links:
                print("❌ Không tìm thấy player links")
                return
            
            print(f"\n📺 Xử lý {min(len(player_links), 5)} streams...\n")
            
            # Xử lý từng player (max 5)
            for i, stream in enumerate(player_links[:5], 1):
                print(f"[{i}] {stream['name']}")
                
                player_html = self.get_page_source(stream['url'], driver)
                
                if not player_html:
                    continue
                
                # Trích xuất stream URL
                stream_urls = self.extract_stream_url(player_html)
                
                if stream_urls:
                    for url in stream_urls:
                        self.all_streams.append({
                            'name': stream['name'],
                            'player_url': stream['url'],
                            'stream_url': url
                        })
                        print(f"  ✓ {url[:70]}...")
                else:
                    print(f"  ⚠️ Không tìm stream URL")
                
                time.sleep(1)
        
        finally:
            driver.quit()

    def save_results(self):
        """Lưu kết quả"""
        print(f"\n📁 Lưu {len(self.all_streams)} streams...")
        
        # M3U
        m3u_file = os.path.join(self.output_dir, 'streams.m3u')
        with open(m3u_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            for stream in self.all_streams:
                f.write(f"#EXTINF:-1,{stream['name']}\n")
                f.write(f"{stream['stream_url']}\n")
        print(f"  ✅ streams.m3u")
        
        # TXT
        txt_file = os.path.join(self.output_dir, 'streams.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            for i, stream in enumerate(self.all_streams, 1):
                f.write(f"{i}. {stream['name']}\n")
                f.write(f"   {stream['stream_url']}\n\n")
        print(f"  ✅ streams.txt")
        
        # JSON
        json_file = os.path.join(self.output_dir, 'streams.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total': len(self.all_streams),
                'streams': self.all_streams
            }, f, ensure_ascii=False, indent=2)
        print(f"  ✅ streams.json")

    def run(self):
        """Chạy"""
        print("\n" + "="*80)
        print("🎬 STREAM EXTRACTOR - streamsports99.su")
        print("="*80)
        
        self.process_streams('https://streamsports99.su/')
        
        if self.all_streams:
            self.save_results()
            print("\n" + "="*80)
            print(f"✅ THÀNH CÔNG! Tìm {len(self.all_streams)} streams")
            print("="*80 + "\n")
        else:
            print("\n" + "="*80)
            print("⚠️ Không tìm thấy streams")
            print("="*80 + "\n")


def main():
    extractor = StreamExtractorSelenium()
    extractor.run()


if __name__ == '__main__':
    main()
