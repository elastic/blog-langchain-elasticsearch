from elasticsearch import Elasticsearch, helpers
import os

es_server = os.environ.get("ES_SERVER")
es_username = os.environ.get("ES_USERNAME")
es_password = os.environ.get("ES_PASSWORD")

batch_size = 25  # Set your desired batch size here

def batchify(docs, batch_size):
    for i in range(0, len(docs), batch_size):
        yield docs[i:i + batch_size]

def bulkLoadIndexPipeline( json_docs, index_name,  pipeline):
    url = f"https://{es_username}:{es_password}@{es_server}:443"
    with Elasticsearch([url], verify_certs=True) as es:

        # doc_type = "_doc"

        # Create the index with the mapping if it doesn't exist
        # if not es.indices.exists(index=index_name):
        #     es.indices.create(index=index_name, body=mapping)

        batches = list(batchify(json_docs, batch_size))

        for batch in batches:
            # Convert the JSON documents to the format required for bulk insertion
            bulk_docs = [
                {
                    "_op_type": "index",
                    "_index": index_name,
                    "_source": doc,
                    "pipeline": pipeline
                }
                for doc in batch
            ]

            # Perform bulk insertion
            success, errors =  helpers.bulk(es, bulk_docs, raise_on_error=False)
            if errors:
                for error in errors:
                    print(error)
                    # print(f"Error in document {error['_id']}: {error['index']['error']}")
                # else:
                    # print(f"Successfully inserted {success} documents.")