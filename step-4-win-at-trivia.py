import lib_llm
import lib_embeddings
import lib_vectordb


print("""
.___  ___.      ___   ____    ____    .___________. __    __   _______     _  _    .___________. __    __  
|   \/   |     /   \  \   \  /   /    |           ||  |  |  | |   ____|   | || |   |           ||  |  |  | 
|  \  /  |    /  ^  \  \   \/   /     `---|  |----`|  |__|  | |  |__      | || |_  `---|  |----`|  |__|  | 
|  |\/|  |   /  /_\  \  \_    _/          |  |     |   __   | |   __|     |__   _|     |  |     |   __   | 
|  |  |  |  /  _____  \   |  |            |  |     |  |  |  | |  |____       | |       |  |     |  |  |  | 
|__|  |__| /__/     \__\  |__|            |__|     |__|  |__| |_______|      |_|       |__|     |__|  |__| 
                                                                                                           
.______    _______    ____    __    ____  __  .___________. __    __     ____    ____  ______    __    __  
|   _  \  |   ____|   \   \  /  \  /   / |  | |           ||  |  |  |    \   \  /   / /  __  \  |  |  |  | 
|  |_)  | |  |__       \   \/    \/   /  |  | `---|  |----`|  |__|  |     \   \/   / |  |  |  | |  |  |  | 
|   _  <  |   __|       \            /   |  |     |  |     |   __   |      \_    _/  |  |  |  | |  |  |  | 
|  |_)  | |  |____       \    /\    /    |  |     |  |     |  |  |  |        |  |    |  `--'  | |  `--'  | 
|______/  |_______|       \__/  \__/     |__|     |__|     |__|  |__|        |__|     \______/   \______/  
                                                                                                           
""")


topic = "Star Wars"
index_name = "book_wookieepedia_mpnet"

# Huggingface embedding setup
hf = lib_embeddings.setup_embeddings()

## Elasticsearch as a vector db
db, url = lib_vectordb.setup_vectordb(hf,index_name)

## set up the conversational LLM
llm_chain_informed= lib_llm.make_the_llm()


## how to ask a question
def ask_a_question(question):
    # print("The Question at hand: "+question)

    ## 3. get the relevant chunk from Elasticsearch for a question
    # print(">> 3. get the relevant chunk from Elasticsearch for a question")
    similar_docs = db.similarity_search(question)
    print(f'The most relevant passage: \n\t{similar_docs[0].page_content}')

    ## 4. Ask Local LLM context informed prompt
    # print(">> 4. Asking The Book ... and its response is: ")
    
    informed_context= similar_docs[0].page_content
    informed_response = llm_chain_informed.run(context=informed_context,question=question)
    
    return informed_response


# The conversational loop

print(f'I am a trivia chat bot, ask me any question about {topic}')

while True:
    command = input("User Question >> ")
    response= ask_a_question(command)
    print(f"\tAnswer  : {response}")

