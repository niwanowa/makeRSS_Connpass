import requests
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def main():
    output_file = "makeRSS_Connpass.xml"
    base_url = "http://connpass.com/explore/"
    url = base_url
    include_words = ["AI", "ChatGPT"]

    print(f"Starting with base URL: {base_url}")

    # 既存のRSSフィードを読み込む
    existing_links = set()
    if os.path.exists(output_file):
        tree = ET.parse(output_file)
        root = tree.getroot()
        for item in root.findall(".//item/link"):
            existing_links.add(item.text)
    else:
        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")
        title = "Connpassからのイベント情報"
        description = "Connpassからのイベント情報を提供します。"
        ET.SubElement(channel, "title").text = title
        ET.SubElement(channel, "description").text = description
        ET.SubElement(channel, "link").text = "https://example.com"

    # 30ページまでスクレイピング
    for page in range(1, 31):
        print(f"Fetching page {page}...")
        
        #response = requests.get(url)
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        
        html_content = response.text
        print(f"Response status code: {response.status_code}")

        
        events_found = 0  # このページで見つかったイベントの数 <- この行を追加
    
        for match in event_pattern.findall(html_content):
            events_found += 1  # この行も追加
            event_html = match

        
        channel = root.find("channel")
        event_pattern = re.compile(r'<div class="recent_event_list">([\s\S]*?)<\/div>\s*<\/div>')

        found_events = event_pattern.findall(html_content)
        print(f"Found {len(found_events)} events on page {page}.")
        
        for match in found_events:
            event_html = match

            date = re.search(r'title="(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"', event_html).group(1)
            title_link = re.search(r'<a class="image_link event_thumb" href="(https:\/\/[a-zA-Z0-9\-\.\/]+)" title="(.*?)">', event_html)
            link, title = title_link.groups()

            # 既存のリンクならスキップ
            if link in existing_links:
                continue

            # 含めたいワードが含まれているかチェック
            if any(word in title for word in include_words):
                new_item = ET.SubElement(channel, "item")
                ET.SubElement(new_item, "title").text = title
                ET.SubElement(new_item, "link").text = link
                ET.SubElement(new_item, "pubDate").text = date

        print(f"Found {events_found} events on page {page}.")  # このページで何件見つかったか出力 <- この行も追加
        
        # 次のページへ
        next_page = re.search(r'<li class="to_next"><a href="\?page=(\d+)">次へ&gt;&gt;<\/a><\/li>', html_content)
        if next_page:
            url = base_url + "?page=" + next_page.group(1)
        else:
            print("No more pages found.")
            break  # 次のページがなければ終了

    xml_str = ET.tostring(root)
    xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_file, "w") as f:
        f.write(xml_pretty_str)

if __name__ == "__main__":
    main()
