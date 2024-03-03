import os
import sys
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse

sys.path.append('.')
import config
from tools import error_handler_common
from logger import main_logger



'''
Functions related to scraping News.

Markdown based on parsed links.
'''


@error_handler_common
def write_news():
    response = requests.get('https://coinqueror.io/?search=bitcoin')
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.find_all('h2')
    
    news_list = []
    check_list = [config.currency_crypto.upper(), config.currency_crypto_ticker.upper(), 'Lightning']
    remove_list = [' - Decrypt',  '| Bitcoinist.com', '- The Daily Hodl']

    for headline in headlines:
        headlines_list = []
        links = headline.find_all('a')
        for link in links:
            link_label = link.get('aria-label')
            for remove_word in remove_list:
                if remove_word in link_label:
                    link_label = link_label.replace(remove_word, '')
            link_url = link['href']
            for check_word in check_list:
                if check_word in link_label.upper():
                    headlines_list.append(link_label)
                    headlines_list.append(link_url)
                    break

        news_list.append(headlines_list)   

    news_path = 'db/news/'
    news_file = news_path + 'news.md'

    if not os.path.isdir(news_path):
        os.makedirs(news_path, exist_ok=True) 

    # Write News to Markdown file:
    with open (news_file, 'w') as markdown:
        news_count = 0
        for news in news_list:
            if news:
                news_count += 1
                name, link = news
                source = urlparse(link).netloc.replace('www.', '').replace('.com', '').replace('.net', '').replace('.co', '').replace('.', ' ')
                markdown.write(f'{news_count}. [{name}]({link}) | {source}\n\n')
        markdown.write(f'\nPowered by [Coinqueror.io](https://coinqueror.io/)')

    main_logger.info(f'[markdown] news text written')

    return news_file




if __name__ == '__main__':

    write_news()
