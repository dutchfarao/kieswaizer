import random
import shutil
import string
import time
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat
from hugchat.login import Login
import pandas as pd
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
from langchain.text_splitter import CharacterTextSplitter
from backend.prompt_template import START_UP_MESSAGE, VOTER_PROFILE_1, VOTER_PROFILE_2, VOTER_PROFILE_3, base_prompt
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from backend.custom_huggingchat import HuggingChat
from langchain.embeddings import HuggingFaceHubEmbeddings
import pdfplumber
import docx2txt


hf = None
repo_id = "sentence-transformers/all-mpnet-base-v2"
input_text = None

if 'hf' not in st.session_state:
    hf = HuggingFaceHubEmbeddings(
        repo_id=repo_id,
        task="feature-extraction",
        huggingfacehub_api_token=st.secrets['HUGGINGFACEHUB_API_TOKEN'],
    ) # type: ignore
    st.session_state['hf'] = hf



st.set_page_config(
    page_title="Kies wijzer, gebruik kieswAIzer 🧠", page_icon="🧠", layout="wide", initial_sidebar_state="expanded"
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






# Sidebar for login and voter profile input
with st.sidebar:
    st.title('Kies wijzer, gebruik kieswAIzer 🧠')
    
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
                            st.info("Are you sure you're an admin? ;)")
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
                    if 'start_up' not in st.session_state:
                        time.sleep(1)
                        st.session_state['start_up'] = [START_UP_MESSAGE]

                    ## generated stores AI generated responses
                    if 'generated' not in st.session_state:
                        st.session_state['generated'] = ["Awesome! Let's start."]
                    ## past stores User's questions
                    if 'past' not in st.session_state:
                        st.session_state['past'] = ["I'm ready!"]

                    st.session_state['LLM'] =  HuggingChat(email=st.session_state['hf_email'], psw=st.session_state['hf_pass'])
                    
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



        if st.session_state['admin_mode'] == 'inactive' and 'pdf' not in st.session_state:
            documents = []
            with st.spinner('Reading political manifestos ...'):
                political_manifestos = open('data/political_parties.txt')
                documents += [political_manifestos.read()]
            st.session_state['documents'] = documents
            # Split documents into chunks
            with st.spinner('Summarizing standpoints and ideals ...'):
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                texts = text_splitter.create_documents(documents)
                # Select embeddings
                embeddings = st.session_state['hf']
                # Create a vectorstore from documents
                random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                db = Chroma.from_documents(texts, embeddings, persist_directory="./chroma_db_" + random_str)
            
            with st.spinner('Almost done ...'):
                # Create retriever interface
                retriever = db.as_retriever()
                # Create QA chain
                qa = RetrievalQA.from_chain_type(llm=st.session_state['LLM'], chain_type='stuff', retriever=retriever,  return_source_documents=True)
                st.session_state['pdf'] = qa

            st.experimental_rerun()




        # Plugin for admin
        if st.session_state['plugin'] == "Upload documents" and 'documents' not in st.session_state:
            with st.expander("Upload documents", expanded=True):  
                upload_pdf = st.file_uploader("Upload your document", type=['txt', 'pdf', 'docx'], accept_multiple_files=True)
                if upload_pdf is not None and st.button('✅ Load Document(s)'):
                    documents = []
                    with st.spinner(' Reading documents...'):
                        for upload_pdf in upload_pdf:
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
    add_vertical_space(2)
    if 'hf_email' in st.session_state:
        if st.button('🗑 Logout'):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.experimental_rerun()

    voter_profile =  st.text_area(label='Type your voter profile here', placeholder=VOTER_PROFILE_2, height=350)
    if 'voter_profile' not in st.session_state:
        st.session_state['voter_profile'] = voter_profile



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
        if len(voter_profile) > 2:
            input_text = st.chat_input("🧑‍💻 Write here 👇", key="input")
        


if st.session_state['admin_mode'] == 'active'and 'pdf' in st.session_state:
    with data_view_container:
            with st.expander(" View your **documents**"):
                st.write(st.session_state['documents'])
            
# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(prompt):
    final_prompt =  ""
    source = ""

    with loading_container:

        if st.session_state['admin_mode'] == 'inactive'and 'pdf' in st.session_state:
            # Process below applies to normal user mode
            context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
            with st.spinner('Comparing your voter profile with party manifestos...'):
                print('PROMPT:-----------',prompt, "ÇONTEXT: ------------------", context,"VPROFILE: ------------------", voter_profile )
                prompt = base_prompt(prompt, context, voter_profile)
                result = st.session_state['pdf']({"query": prompt})
                solution = result["result"]
                final_prompt = solution
                if 'source_documents' in result and len(result["source_documents"]) > 0:
                    final_prompt += "\n\n✅Source:\n" 
                    for d in result["source_documents"]:
                        final_prompt += "- " + str(d) + "\n"
              




        else:
            # Process below applies to admin mode
            if st.session_state['plugin'] == "Upload documents" and 'pdf' in st.session_state:
                context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
                with st.spinner('🚀 Using tool to get information...'):
                    result = st.session_state['pdf']({"query": prompt})
                    solution = result["result"]
                    final_prompt = solution
                    if 'source_documents' in result and len(result["source_documents"]) > 0:
                        final_prompt += "\n\n✅Source:\n" 
                        for d in result["source_documents"]:
                            final_prompt += "- " + str(d) + "\n"
            
            else:
                #get last message if exists
                if len(st.session_state['past']) == 1:
                    context = f"User: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
                else:
                    context = f"User: {st.session_state['past'][-2]}\nBot: {st.session_state['generated'][-2]}\nUser: {st.session_state['past'][-1]}\nBot: {st.session_state['generated'][-1]}\n"
                
                final_prompt = base_prompt(prompt, context, "")



        with st.spinner('Writing response ...'):
            response = final_prompt            

    return response

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if input_text is not None and 'hf_email' in st.session_state and 'hf_pass' in st.session_state:
        response = generate_response(input_text)
        print(input_text)
        print(response)
        st.session_state.past.append(input_text)
        st.session_state.generated.append(response)
    

#print message in normal order, first user then bot
    if 'start_up' in st.session_state:
        for i in range(len(st.session_state['start_up'])):
            st.session_state['voter_profile'] = voter_profile
            with st.chat_message(name="assistant"):
                time.sleep(2)
                st.markdown(st.session_state['start_up'][i])
            if len(st.session_state['voter_profile']) > 2:
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
                st.error("You can start chatting after you've completed your voter profile. Do this in the sidebar on the left 👈")
            
    else:
        st.info("👋 Hey , happy to see that you're planning to vote the upcoming elections!")
        st.info("👉 Please login on the right to continue. ")
        st.error("👉 If you are not registered on Hugging Face, please register first and then login 🤗")