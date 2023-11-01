from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

def main():
    p = sync_playwright().start()

    # Use pandas to load the csv file
    df = pd.read_csv('unclaimed.csv')

    browser = p.chromium.launch(headless=False)
    

    try:
        # Loop through each address that has not been marked as processed
        for i, row in df.loc[df['processed'] == False].iterrows():
            address = row['source']
            
            page = browser.new_page()
            page.goto("https://opensea.io/" + address, timeout=0)
            
            # We use BeautifulSoup to parse the HTML and extract the desired elements
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            # Find username (h1 tag), store it only if it's not 'Unnamed'
            username = soup.find('div', class_='sc-beff130f-0 sc-630fc9ab-0 sc-6911ed2f-1 dYQlaY bNkKFC iFpewb').find_all('h1')[0]
            print(username)
            if username is not None and username.text != 'Unnamed':
                df.loc[i, 'name'] = username.text

            # Find socials (a tags in the specified div), store href values
            div = soup.find('div', class_='sc-beff130f-0 sc-630fc9ab-0 sc-968937a5-0 hksMfk bNkKFC cNAoge')
            socials = div.find_all('a') if div is not None else []
            df.loc[i, 'socials'] = ', '.join([s.get('href') for s in socials])
            
            # Mark this row as processed
            df.loc[i, 'processed'] = True

            df.to_csv('unclaimed.csv', index=False)
            page.close()

    finally:
        browser.close()
        p.stop()
        
    

main()