import io
import random
import shutil
import string
from zipfile import ZipFile
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from hugchat.login import Login
import pandas as pd
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
from langchain.text_splitter import CharacterTextSplitter
from backend.prompt_template import prompt4Code, prompt4Context,  prompt4conversation
# from backend.promptTemplate import prompt4conversationInternet, prompt4conversation
# FOR DEVELOPMENT NEW PLUGIN 
# from promptTemplate import yourPLUGIN
# from exportchat import export_chat
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from backend.custom_huggingchat import CustomHuggingChat
from langchain.embeddings import HuggingFaceHubEmbeddings
# from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import pdfplumber
import docx2txt
# from duckduckgo_search import DDGS
from itertools import islice
from os import path
# from pydub import AudioSegment
import os


hf = None
repo_id = "sentence-transformers/all-mpnet-base-v2"

if 'hf' not in st.session_state:
    hf = HuggingFaceHubEmbeddings(
        repo_id=repo_id,
        task="feature-extraction",
        huggingfacehub_api_token=st.secrets['HUGGINGFACEHUB_API_TOKEN'],
    ) # type: ignore
    st.session_state['hf'] = hf



st.set_page_config(
    page_title="Kies wijzer, gebruik kieswAIzer💬", page_icon="🧠", layout="wide", initial_sidebar_state="expanded"
)

st.markdown('<style>.css-w770g5{\
            width: 100%;}\
            .css-b3z5c9{    \
            width: 100%;}\
            .stButton>button{\
            width: 100%;}\
            .stDownloadButton>button{\
            width: 100%;}\
            </style>', unsafe_allow_html=True)






# Sidebar contents for logIN, choose plugin, and export chat
with st.sidebar:
    st.title('🧠 StemwAIzer 🧠')
    
    if 'hf_email' not in st.session_state or 'hf_pass' not in st.session_state:
        st.session_state['admin_mode'] = 'inactive'
        with st.expander("ℹ️ Hugging Face login", expanded=True):
            st.write("⚠️ You need to login in Hugging Face to use this app. You can register [here](https://huggingface.co/join).")
            st.header('Hugging Face Login')
            hf_email = st.text_input('Enter E-mail:', type= 'default')
            hf_pass = st.text_input('Enter password:', type='password')

            
            if st.checkbox('admin'):
                admin_pass = st.text_input('Enter admin credentials:', type='password')
                st.session_state['admin_pass'] = admin_pass
            else: 
                admin_pass = None
            if st.button('Login 🚀') and hf_email and hf_pass: 
                with st.spinner('🚀 Logging in...'):
                    st.session_state['hf_email'] = hf_email
                    st.session_state['hf_pass'] = hf_pass
                    try:
                        sign = Login(st.session_state['hf_email'], st.session_state['hf_pass'])
                        cookies = sign.login()
                        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
                    except Exception as e:
                        st.error(e)
                        st.info("⚠️ Please check your credentials and try again.")
                        st.warning("⚠️ If you don't have an account, you can register [here](https://huggingface.co/join).")
                        from time import sleep
                        sleep(3)
                        del st.session_state['hf_email']
                        del st.session_state['hf_pass']
                        st.experimental_rerun()
                    if admin_pass:
                        try:
                            assert admin_pass == st.secrets['admin_pass']
                            st.session_state['admin_mode'] = 'active'
                        except AssertionError as e:
                            st.error(e)
                            st.info("⚠️ Please check your credentials and try again.")
                            from time import sleep
                            sleep(3)
                            del st.session_state['hf_email']
                            del st.session_state['hf_pass']
                            del st.session_state['admin_pass']
                            del st.session_state['admin_mode']
                            st.experimental_rerun()


                    st.session_state['chatbot'] = chatbot

                    id = st.session_state['chatbot'].new_conversation()
                    st.session_state['chatbot'].change_conversation(id)

                    st.session_state['conversation'] = id
                    # Generate empty lists for generated and past.
                    ## generated stores AI generated responses
                    if 'generated' not in st.session_state:
                        st.session_state['generated'] = ["Hi there, I'm **KieswAIzer**, How may I help you ? "]
                    ## past stores User's questions
                    if 'past' not in st.session_state:
                        st.session_state['past'] = ['Hi!']

                    st.session_state['LLM'] =  CustomHuggingChat(email=st.session_state['hf_email'], psw=st.session_state['hf_pass'])
                    
                    st.experimental_rerun()
                        

    else:
        st.session_state['plugin'] = 'non_admin'
        if st.session_state['admin_mode'] == 'active':
            #plugins for admin mode
            plugins = ["🛑 No PLUGIN", "Upload documents","Upload saved VectorStore"]
            st.session_state['plugin'] = 'init'
            if st.session_state['plugin'] == 'init':
                st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=0)
            else:
                if st.session_state['plugin'] == "🛑 No PLUGIN":
                    st.session_state['plugin'] = st.selectbox('🔌 Plugins', plugins, index=plugins.index(st.session_state['plugin']))




    # DOCUMENTS PLUGIN
            if st.session_state['plugin'] == "Upload documents" and 'documents' not in st.session_state:
                with st.expander("Upload documents", expanded=True):  
                    upload_pdf = st.file_uploader("Upload your document", type=['txt', 'pdf', 'docx'], accept_multiple_files=True)
                    if upload_pdf is not None and st.button('✅ Load Document(s)'):
                        documents = []
                        with st.spinner(' Reading documents...'):
                            for upload_pdf in upload_pdf:
                                print(upload_pdf.type)
                                if upload_pdf.type == 'text/plain':
                                    documents += [upload_pdf.read().decode()]
                                elif upload_pdf.type == 'application/pdf':
                                    with pdfplumber.open(upload_pdf) as pdf:
                                        documents += [page.extract_text() for page in pdf.pages]
                                elif upload_pdf.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                    text = docx2txt.process(upload_pdf)
                                    documents += [text]
                        st.session_state['documents'] = documents
                        # Split documents into chunks
                        with st.spinner('🔨 Creating vectorstore...'):
                            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                            texts = text_splitter.create_documents(documents)
                            # Select embeddings
                            embeddings = st.session_state['hf']
                            # Create a vectorstore from documents
                            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                            db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)

                        with st.spinner('🔨 Saving vectorstore...'):
                            # save vectorstore
                            db.persist()
                            #create .zip file of directory to download
                            shutil.make_archive("./chroma_db_" + random_str, 'zip', "./chroma_db_" + random_str)
                            # save in session state and download
                            st.session_state['db'] = "./chroma_db_" + random_str + ".zip" 
                        
                        with st.spinner('🔨 Creating QA chain...'):
                            # Create retriever interface
                            retriever = db.as_retriever()
                            # Create QA chain
                            qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever,  return_source_documents=True)
                            st.session_state['pdf'] = qa

                        st.experimental_rerun()

            if st.session_state['plugin'] == "Upload documents":
                if 'db' in st.session_state:
                    # leave ./ from name for download
                    file_name = st.session_state['db'][2:]
                    st.download_button(
                        label="📩 Download vectorstore",
                        data=open(file_name, 'rb').read(),
                        file_name=file_name,
                        mime='application/zip'
                    )
                if st.button('🛑 Remove document from context'):
                    if 'pdf' in st.session_state:
                        del st.session_state['db']
                        del st.session_state['pdf']
                        del st.session_state['documents']
                    del st.session_state['plugin']
                        
                    st.experimental_rerun()

# END OF PLUGIN
    add_vertical_space(4)
    if 'hf_email' in st.session_state:
        if st.button('🗑 Logout'):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.experimental_rerun()

    # export_chat()
    add_vertical_space(5)

##### End of sidebar


# User input
# Layout of input/response containers
input_container = st.container()
response_container = st.container()
data_view_container = st.container()
loading_container = st.container()



## Applying the user input box
with input_container:
        input_text = st.chat_input("🧑‍💻 Write here 👇", key="input")

with data_view_container:
    if 'pdf' in st.session_state:
        with st.expander(" View your **documents**"):
            st.write(st.session_state['documents'])
            
# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    final_prompt =  ""
    source = ""

    with loading_container:

        if st.session_state['plugin'] == "Upload documents" and 'pdf' in st.session_state:
            #get only last message
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('🚀 Using tool to get information...'):
                result = st.session_state['pdf']({"query": prompt})
                solution = result["result"]
                if len(solution.split()) > 110:
                    make_better = False
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
                else:
                    final_prompt = prompt4Context(prompt, context, solution)
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        source += "\n\n✅Source:\n"
                        for d in result["source_documents"]:
                            source += "- " + str(d) + "\n"                    
        else:
            #get last message if exists
            if len(st.session_state['past']) == 1:
                context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            else:
                context = f"User: {st.session_state['past'][-2]}\nBot: {st.session_state['generated'][-2]}\nUser: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            
            final_prompt = prompt4conversation(prompt, context)



        with st.spinner('🚀 Generating response...'):
            response = final_prompt            

    return response

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if input_text and 'hf_email' in st.session_state and 'hf_pass' in st.session_state:
        response = generate_response(input_text)
        st.session_state.past.append(input_text)
        st.session_state.generated.append(response)
    

    #print message in normal order, first user then bot
    if 'generated' in st.session_state:
        print(st.session_state)
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                with st.chat_message(name="user"):
                    st.markdown(st.session_state['past'][i])
                
                with st.chat_message(name="assistant"):
                    if len(st.session_state['generated'][i].split("✅Source:")) > 1:
                        source = st.session_state['generated'][i].split("✅Source:")[1]
                        mess = st.session_state['generated'][i].split("✅Source:")[0]

                        st.markdown(mess)
                        with st.expander("📚 Source of message number " + str(i+1)):
                            st.markdown(source)

                    else:
                        st.markdown(st.session_state['generated'][i])

            st.markdown('', unsafe_allow_html=True)
            
            
    else:
        st.info("👋 Hey , we are very happy to see you here 🤗")
        st.info("👉 Please Login to continue, click on top left corner to login 🚀")
        st.error("👉 If you are not registered on Hugging Face, please register first and then login 🤗")