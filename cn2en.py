import os
import re
import termcolor
import argparse
from googletrans import Translator
translator = Translator()
# import requests
# import re
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from tqdm import tqdm
# import subprocess

def parse_playlist(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    entries = []
    entry = []
    for line in lines:
        if line.startswith('#EXTINF'):
            channel_name = line.split(',')[1]
            translated_name = translator.translate(channel_name, src='zh-CN', dest='en').text
            translated_line = f"{line.split(',')[0]}, {translated_name}"
            if entry:
                entries.append(entry)
            entry = [translated_line]
        elif line.strip():
            entry.append(line)

    if entry:
        entries.append(entry)

    return entries

def write_playlist(file_path, entries):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')
        for entry in entries:
            for line in entry:
                file.write(line)
            file.write('\n')  # Ensure there is a single newline after each entry

def main():
    input_path = "IPTV.m3u"
    output_path = "enIPTV.m3u"
    
    print("Parsing playlist...")
    entries = parse_playlist(input_path)

    # print("Translate cn 2 en ...")
    # valid_entries = translate_channel_names(input_path)

    print("Writing sorted playlist...")
    write_playlist(output_path, entries)
    print("Process completed.")

if __name__ == '__main__':
    main()
