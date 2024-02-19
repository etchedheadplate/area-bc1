import re
import os
import sys
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse

sys.path.append('.')
import config
from logger import main_logger


def write_news():
    response = requests.get('https://coinqueror.io/?search=bitcoin')
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.find_all('h2')
    
    news_list = []
    check_list = [config.currency_crypto.upper(), config.currency_crypto_ticker.upper()]
    for headline in headlines:
        headlines_list = []
        links = headline.find_all('a')
        for link in links:
            link_label = link.get('aria-label')
            link_url = link['href']
            for word in check_list:
                pattern = re.compile(fr'{re.escape(word)}(?![a-zA-Z])')
                if pattern.match(link_label.upper()):
                    headlines_list.append(link_label)
                    headlines_list.append(link_url)
                    break
            else:
                headlines_list.append(link_label)
                headlines_list.append(link_url)

        news_list.append(headlines_list)   

    news_path = 'db/news/'
    news_file = news_path + 'news.md'

    if not os.path.isdir(news_path):
        os.makedirs(news_path, exist_ok=True) 

    # Write News to Markdown file:
    with open (news_file, 'w') as markdown:
        for news in news_list:
            if news:
                name, link = news
                source = urlparse(link).netloc.replace('www.', '').replace('.', ' ').replace('com', '')
                markdown.write(f'[{name}]({link}) | {source}\n\n')

    main_logger.info(f'[markdown] news text written')

    return news_file




if __name__ == '__main__':

    write_news()
