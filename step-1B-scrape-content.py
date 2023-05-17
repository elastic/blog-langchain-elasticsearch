import re
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup 
import pickle
import json

print("""
  ______   ______   .__   __. .___________. _______ .__   __. .___________.
 /      | /  __  \  |  \ |  | |           ||   ____||  \ |  | |           |
|  ,----'|  |  |  | |   \|  | `---|  |----`|  |__   |   \|  | `---|  |----`
|  |     |  |  |  | |  . `  |     |  |     |   __|  |  . `  |     |  |     
|  `----.|  `--'  | |  |\   |     |  |     |  |____ |  |\   |     |  |     
 \______| \______/  |__| \__|     |__|     |_______||__| \__|     |__|     
                                                                           
""")


scraped = {}
failed = {}
partition_size = 5000
folder = './Dataset/'

with open('./Dataset/starwars_all_canon_dict.pickle', 'rb') as f:
    pages = pickle.load(f)

last_number = 0
for ix, (key, page_url) in tqdm(enumerate(pages.items()), total=(len(pages))):
    try:
        
        # Get page
        result = requests.get(page_url)
        content = result.content
        soup = BeautifulSoup(content, "html.parser")

        # Get title
        heading = soup.find('h1', id='firstHeading')
        if heading is None: continue
        heading = heading.text

        # Extract Sidebar
        is_character = False
        side_bar = {}
        sec = soup.find_all('section', class_='pi-item')
        for s in sec:
            title = s.find('h2')
            if title is None:
                title = '<no category>'
            else:
                title = title.text
            side_bar[title] = {}
            items = s.find_all('div', class_='pi-item')
            for item in items:
                attr = item.find('h3', class_='pi-data-label')
                if attr is None:
                    attr = '<no attribute>'
                else:
                    attr = attr.text
                if attr == 'Species': is_character = True
                value = re.sub("[\(\[].*?[\)\]]" ,'', '], '.join(item.find('div', class_='pi-data-value').text.split(']')))
                value = value.strip()[:-1].replace(',,', ',')
                if ',' in value:
                    value = [i.strip() for i in value.split(',') if i.strip() != '']
                side_bar[title][attr] = value

        # Raw page content
        raw_content = soup.find('div', class_='mw-parser-output')
        if raw_content is not None:
            content_pgs = []
            for raw_paragraph in raw_content.find_all('p', recursive=False):
                if 'aside' in str(raw_paragraph): continue
                content_pgs.append(re.sub("[\(\[].*?[\)\]]" ,'', raw_paragraph.text) )
            # paragraph = value = re.sub("[\(\[].*?[\)\]]" ,'', raw_paragraph.text)

            # cross-links
            keywords = []
            for link in raw_content.find_all('a'):
                part = link.get('href')
                if part is not None:
                    part = part.split('/')[-1] 
                    if part in pages.keys() and part != key:
                        keywords.append(part)
            keywords = list(set(keywords))
        else:
            # Empty page
            keywords = []
            paragraph = ''

        # Data object
        scraped[key] = {
            'url': page_url,
            'title': heading,
            'is_character': is_character,
            'side_bar': side_bar,
            'paragraph': content_pgs,
            'crosslinks': keywords,
        }

        # print(json.dumps(scraped[key],indent=4))

        
        # save partition
        if (ix + 1) % partition_size == 0:
            last_number = (ix+1) // partition_size
            fn = folder + f'starwars_all_canon_data_{last_number}.pickle'
            with open(fn, 'wb') as f:
                pickle.dump(scraped, f, protocol=pickle.HIGHEST_PROTOCOL)
            scraped = {}
    except:
        print('Failed!')
        failed[key] = page_url
    
# Save final part to disk
if 'last_number' not in locals():
    last_number = 0
fn = folder + f'starwars_all_canon_data_{last_number + 1}.pickle'
with open(fn, 'wb') as f:
    pickle.dump(scraped, f, protocol=pickle.HIGHEST_PROTOCOL)