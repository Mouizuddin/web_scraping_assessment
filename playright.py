from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
data_dict = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://quotes.toscrape.com/login')
    page.fill('input#username','mx new')
    page.fill('input#password','123@#')
    page.click('input[type=submit]')
    # page.wait_for_timeout(4000)
    html_content = page.content()
    code = BeautifulSoup(html_content, 'html.parser')
  
    quote_div = code.find_all('div',{'class':'col-md-8'})[1]
    all_quotes = [x.get_text(strip=True) for x in quote_div.find_all('span',{'class':'text'})]
    author = [x.get_text(strip=True) for x in quote_div.find_all('small',{'class':'author'})]
    about_author_urls = ['https://quotes.toscrape.com'+x.find_next('a')['href'] for x in quote_div.find_all('span',{'class':'text'}) ]
    
    
    # data_dict['tag_choosen'] = choosen_tag
    data_dict['author'] = author
    data_dict['quote'] = all_quotes
    data_dict['about_author'] = about_author_urls


df = pd.DataFrame(data_dict)
print(df.shape)
print(df.head)
# df.to_csv('data.csv', index=False)

    