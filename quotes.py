import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests



st.title('MX screaning test')

st.header('Web scraping streamlit application', divider='rainbow')
st.write("")
def get_tags():
    link = requests.get('https://quotes.toscrape.com/').text
    code = BeautifulSoup(link, 'html.parser')
    tags_div = code.find('div',{'class':'col-md-4 tags-box'})
    tags = [x.text.strip() for x in tags_div.find_all('a')]
    return tags

all_tag_names = get_tags()

choosen_tag = st.selectbox('Choose a tag', all_tag_names, index=None)
if choosen_tag:
    to_scrape_url = f"https://quotes.toscrape.com/tag/{choosen_tag}/"
    st.write(f'scraping this link >> {to_scrape_url}')

def scraper(pass_link):
    link = requests.get(pass_link).text
    code = BeautifulSoup(link, 'html.parser')    
    quote_div = code.find_all('div',{'class':'col-md-8'})[1]
    all_quotes = [x.get_text(strip=True) for x in quote_div.find_all('span',{'class':'text'})]
    author = [x.get_text(strip=True) for x in quote_div.find_all('small',{'class':'author'})]
    about_author_urls = ['https://quotes.toscrape.com'+x.find_next('a')['href'] for x in quote_div.find_all('span',{'class':'text'}) ]
    data_dict = {}
    
    data_dict['tag_choosen'] = choosen_tag
    data_dict['author'] = author
    data_dict['quote'] = all_quotes
    data_dict['about_author'] = about_author_urls
    return pd.DataFrame(data_dict)

if choosen_tag:
    scraped_quotes_by_tag = scraper(to_scrape_url)
    data_frame = st.dataframe(scraped_quotes_by_tag)

    get_csv = st.button('Download CSV')
    if get_csv:
        try:
            scraped_quotes_by_tag.to_csv(f'{choosen_tag}.csv', index=False)
        except:
                st.write('Error in generating CSV')


