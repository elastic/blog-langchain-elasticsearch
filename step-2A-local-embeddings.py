import os

import lib_embeddings
import lib_vectordb

from pathlib import Path
import pickle

from elasticsearch import Elasticsearch
from tqdm import tqdm

print("""
____    ____  _______   ______ .___________.  ______   .______      
\   \  /   / |   ____| /      ||           | /  __  \  |   _  \     
 \   \/   /  |  |__   |  ,----'`---|  |----`|  |  |  | |  |_)  |    
  \      /   |   __|  |  |         |  |     |  |  |  | |      /     
   \    /    |  |____ |  `----.    |  |     |  `--'  | |  |\  \----.
    \__/     |_______| \______|    |__|      \______/  | _| `._____|
                                                                    
""")


bookFilePath = "starwars_all_canon_data_*.pickle"
index_name = "book_wookieepedia_test"

## Prepp the local transformer
hf = lib_embeddings.setup_embeddings()

## Elasticsearch as a vector db
db, url = lib_vectordb.setup_vectordb(hf,index_name)

count = 0
files = sorted(Path('./Dataset').glob(bookFilePath))
for fn in files:
    print(f"Starting book: {fn}")
    with open(fn,'rb') as f:
        part = pickle.load(f)
        batchtext = []
        for ix, (key, value) in tqdm(enumerate(part.items()), total=len(part)):
            title = value['title'].strip()
            sw_url = value['url']
            paragraphs = value['paragraph']
            for px, p in enumerate(paragraphs):
                # print(f"{ix} {px} {title}")
                batchtext.append(p)
                count = count + 1
            if len(batchtext) >= 100:
                db.from_texts(batchtext, embedding=hf, elasticsearch_url=url, index_name=index_name)
                batchtext = []
        db.from_texts(batchtext, embedding=hf, elasticsearch_url=url, index_name=index_name)
        batchtext = []
        print(f"Count {count}")


