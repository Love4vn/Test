import os
import re
import termcolor
import argparse
from googletrans import Translator
translator = Translator()

# import requests
# from io import StringIO
# from ipytv import playlist
# from googletrans import Translator

def translate_channel_names(m3u_content):
    # Initialize the Google API translator
    translator = Translator()
    translated_lines = []

    # Load the M3U content
    pl = playlist.loads(m3u_content)

    # Translate channel names and group titles
    for line in m3u_content.splitlines():
        if line.startswith('#EXTINF:'):
            channel_name = line.split(',')[1]
            translated_name = translator.translate(channel_name, src='zh-CN', dest='en').text
            translated_line = f"{line.split(',')[0]}, {translated_name}"
            translated_lines.append(translated_line)
        else:
            translated_lines.append(line)

    return '\n'.join(translated_lines)

if __name__ == "__main__":
   
    token = ''
    owner = 'Love4vn'
    repo = 'Test'
    path = 'https://raw.githubusercontent.com/Love4vn/Test/main/IPTV.m3u'

    # Send a request to GitHub API to get the raw M3U content
    r = requests.get(f'https://api.github.com/repos/{owner}/{repo}/contents/{path}',
                     headers={'accept': 'application/vnd.github.v3.raw', 'authorization': f'token {token}'})

    # Translate channel names and group titles
    translated_m3u = translate_channel_names(m3u_content)

    # Save the translated M3U content to a new file
    with open("https://raw.githubusercontent.com/Love4vn/Test/main/enIPTV.m3u", "w") as output_file:
    output_file.write(translated_m3u)
