import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import logging
from tqdm.contrib.concurrent import thread_map



st.header('MX screening test', divider='rainbow')

st.header('Ecommerece scrapper', divider='rainbow')

st.write("")
st.write("Scraping books category tags...")
def get_tags():
    try:
        link = requests.get('https://books.toscrape.com/catalogue/category/books_1/index.html')
        st.write(f'Status code of the link >> {link.status_code}')
        code = BeautifulSoup(link.text, 'html.parser')
        books_tags = [x.find('a').text.strip() for x in code.find('ul',{'class':'nav nav-list'}).find_all('li')[1:]]
        clean_tags = ['-'.join(tag.lower().split()) for tag in books_tags]
        to_use_tags = []
        for number in enumerate(clean_tags,start=2):
            id, value = number
            url_tag = f"{value.lower()}_{id}"
            to_use_tags.append(url_tag)
        return to_use_tags
    except Exception as e:
            st.write(f"Error in link: {e}")
            logging.error(f"Error in link: {e}")
            


st.write("")
book_category = get_tags()
choosen_tag = st.selectbox('Choose a tag', book_category, index=None)

if choosen_tag:
    to_scrape_url = f"https://books.toscrape.com/catalogue/category/books/{choosen_tag}/index.html"
    st.write(f'scraping this link >> {to_scrape_url}')

    def get_total_products(pass_link):
        try:
            link_book = requests.get(pass_link)
            code_book = BeautifulSoup(link_book.text, 'html.parser')
            total_products = code_book.find('div',{'id':'promotions'}).find_next().find('strong').text.strip()
            return total_products
        except Exception as e:
            st.write(f"Error in link: {e}")
            logging.error(f"Error in link: {e}")



    def pagination(pass_link):
        try:
            link_book = requests.get(pass_link)
            code_book = BeautifulSoup(link_book.text, 'html.parser')
            
            pagination_urls = []
            if code_book.find('li',{'class':'current'}):
                pagination = int(code_book.find('li',{'class':'current'}).text.strip().split('of')[-1].strip())
                for i in range(1,pagination+1):
                    # url = f"https://books.toscrape.com/catalogue/category/books/mystery_3/page-{i}.html"
                    fine_urls = link_book.url.replace('index.html',f'page-{i}.html')
                    # print(fine_urls)
                    pagination_urls.append(fine_urls)
            else:
                pagination_urls.append(link_book.url)
            
            return pagination_urls
        except Exception as e:
            st.write(f"Error in link: {e}")
            logging.error(f"Error in link: {e}")


    total_products = get_total_products(to_scrape_url)  
    pagination_in_products = pagination(to_scrape_url)

    if len(pagination_in_products) >= 1:
        st.write(f'selected link have total  >> {len(pagination_in_products)} page and {total_products} products' )
    else:
        st.write(f'selected link have total  >> {len(pagination_in_products)} page and {total_products} products' )

    def get_all_product_links(pass_link):
        try:
            link = requests.get(pass_link)
            code = BeautifulSoup(link.text, 'html.parser')
            total_products = code.find('div',{'id':'promotions'}).find_next().find('strong').text.strip()
            main_div = code.find('ol',{'class':'row'})
            product_link = ['https://books.toscrape.com/catalogue/'+x.find('a')['href'].replace('../../../','') for x in main_div.find_all('h3')]
            return product_link
        except Exception as e:
            st.write(f"Error in link: {e}")
            logging.error(f"Error in link: {e}")

    
    get_all_links_from_site = thread_map(get_all_product_links, pagination_in_products)
    to_scrape = [x for y in get_all_links_from_site for x in y]
    
    st.write(f'These are the link going to scrape >> {to_scrape}')

    def scraper(pass_link):
        try:

            meta_data = {}
            inner_page = requests.get(pass_link).text
            inner_page_code = BeautifulSoup(inner_page, 'html.parser')
            des = inner_page_code.find('div',{'id':'product_description'}).find_next('p').text.strip()
            warning_text = inner_page_code.find('div',{'class':'alert alert-warning'}).text.strip()
            title = inner_page_code.find('h1').text.strip()
            meta_data['title'] = title
            meta_data['Product Description'] = des
            meta_data['Product Link'] = pass_link
            book_type = inner_page_code.find('ul',{'class':'breadcrumb'}).find_all('li')[2].text.strip()
            meta_data['Book Category'] = book_type
            table = inner_page_code.find('table',{'class':'table table-striped'})
            th = [x.find('th').text.strip() for x in table.find_all('tr')]
            td = [x.find('td').text.strip() for x in table.find_all('tr')]
            table_dict = dict(zip(th,td))
            meta_data['Alert text'] =warning_text
            meta_data.update(table_dict)
            # df = pd.DataFrame(meta_data)
            return meta_data
        except Exception as e:
            st.write(f"Error in link: {e}")
            logging.error(f"Error in link: {e}")

        
    test_scraper = thread_map(scraper, to_scrape)
    data_frame = st.dataframe(test_scraper)
    st.write(f'Data Frame shape >> {pd.DataFrame(test_scraper).shape}')
    download_df = pd.DataFrame(test_scraper)

    get_csv = st.button('Download CSV')
    if get_csv:
        try:
            download_df.to_csv(f'{choosen_tag}.csv', index=False)
        except:
                st.write('Error in generating CSV')



