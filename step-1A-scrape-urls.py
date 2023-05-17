import requests
from bs4 import BeautifulSoup 
import pickle

print("""
     _______.  ______ .______          ___      .______    _______ 
    /       | /      ||   _  \        /   \     |   _  \  |   ____|
   |   (----`|  ,----'|  |_)  |      /  ^  \    |  |_)  | |  |__   
    \   \    |  |     |      /      /  /_\  \   |   ___/  |   __|  
.----)   |   |  `----.|  |\  \----./  _____  \  |  |      |  |____ 
|_______/     \______|| _| `._____/__/     \__\ | _|      |_______|
                                                                   
""")


page_url = 'https://starwars.fandom.com/wiki/Category:Canon_articles'  # all canon articles
base_url = 'https://starwars.fandom.com'

pages = {}
page_num = 1
while page_url is not None:
    result = requests.get(page_url)
    content = result.content
    soup = BeautifulSoup(content, "html.parser")
    
    # extract urls
    links = soup.find_all('a', class_='category-page__member-link')
    links_before = len(pages)
    if links:
        for link in links:
            url = base_url + link.get('href')
            key = link.get('href').split('/')[-1]
            if 'Category:' not in key:
                pages[key] = url
    new_links = len(pages) - links_before
    print(f'Page {page_num} - {new_links} new links ({page_url})')
    page_num += 1
    # get next page button
    next_urls = soup.find_all("a", class_='category-page__pagination-next')
    if next_urls:
        new_url = next_urls[0].get('href')
        if new_url == page_url:
            break
        else:
            page_url = new_url
    else:
        page_url = None



print(f'Number of pages: {len(pages)}')

# Save to disk
with open('./Dataset/starwars_all_canon_dict.pickle', 'wb') as f:
    pickle.dump(pages, f, protocol=pickle.HIGHEST_PROTOCOL)