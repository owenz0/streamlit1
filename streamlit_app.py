import streamlit as st
import chromadb
from groq import Groq
if ("current_chat_id") not in st.session_state:
    st.session_state.current_chat_id = 1
if ("chats") not in st.session_state:
    first_chat_id= 1
    st.session_state.chats = {
        first_chat_id:{"busy":False,"title":"Conversation 1","msg":[{"role":"assistant","content":"Hello World!\nHow can I help you today?"}],"docs":[]}
    }

with st.sidebar:
    st.title("Settings")
    model = st.selectbox("Choose a model: ",["Meta Llama 3.1","OpenAI OSS 20B","OpenAI OSS 120B"])
    if (st.sidebar.button("Create new chat")):
        new_chat_id = max(st.session_state.chats.keys())+1
        st.session_state.chats[new_chat_id]= {"busy":False,"title":"Conversation "+str(new_chat_id),"msg":[{"role":"assistant","content":"Hello World!\nHow can I help you today?"}],"docs":[]}
        st.session_state.current_chat_id = new_chat_id
        st.rerun()
    st.sidebar.write("Chat History")
    for chat_id,chat_data in list(st.session_state.chats.items()):
        is_active = chat_id == (st.session_state.current_chat_id)
        if (is_active):
            button = st.sidebar.button(f"{chat_data["title"]}",type = "primary",key = chat_id)
        else:
            button = st.sidebar.button(f"{chat_data["title"]}",key=chat_id)
        if button:
            st.session_state.current_chat_id = chat_id
            st.rerun()


API_KEY = st.secrets["GROQ_API_KEY"] #use only for streamlit
model_call = {"Meta Llama 3.1":"llama-3.1-8b-instant","OpenAI OSS 20B":"openai/gpt-oss-20b","OpenAI OSS 120B":"openai/gpt-oss-120b"}
# st.write("Hello World!")
MODEL = model_call[model]
groq_client = Groq(api_key = API_KEY)

# if ("msg") not in st.session_state:
#     st.session_state.msg = [{"role":"assistant","content":"Hello World!\nHow can I help you today?"}]
# if ("busy") not in st.session_state:
#     st.session_state.busy = False
# if ("docs") not in st.session_state:
#     st.session_state.docs = []
# if ("file_docs") not in st.session_state:
    # st.session_state.file_docs = []
st.title("CHATBOT!")
# st.write((client.chat.completions.create(model = MODEL, messages = [{"role":"user","content":"hi"}])).choices[0].message.content)
# if ("documents") not in st.session_state:
#     st.session_state.documents = [
#     "The secret code is 4391",
#     "Are dogs good pets?",
#     "Dogs are playful pets.",
#     "Machine learning shows how computers learn.",
#     "Basketball is a good sport.",
#     "Dogs can be friendly companions.",
#     "Dogs are fun pets.",
#     "Dogs are fun pets"
# ]
# if submit_files and uploaded_file and st.session_state.busy == False:
#     st.session_state.busy = True
#     for file in uploaded_file:
#         text = file.read().decode("utf-8")
#         #highly customizable/ by chunks
#         chunks = text.split('\n')
#         st.sidebar.write(len(chunks))
#         client = chromadb.Client()
#         tags = [str(i) for i in range(len(chunks))]
#         collection = client.get_or_create_collection("documents")
#         collection.add(documents=chunks,ids=tags)
#         st.sidebar.write("Chunks added to knowledge base")
#         result = collection.query(query_texts = question,nresults = 3)
#         st.session_state.docs.append({"role":"user","content":file.read().decode("utf-8")})
#         st.session_state.msg.append({"role":"assistant","content":"Files received!"})
#         with st.sidebar:
#             st.toast("Files uploaded successfully!")
#     st.session_state.busy = False
curr = st.session_state.chats[st.session_state.current_chat_id]   
for message in curr["msg"]:
    with st.chat_message(message["role"],avatar = message.get("avatar")):
        st.write(message["content"])
if not curr["busy"]:
    question = st.chat_input("Prompt: ",accept_file = "multiple",file_type=["txt"])
    if question:
        curr["busy"] = True
        st.balloons()
        with (st.spinner()):
            chroma_client = chromadb.Client()
            collection = chroma_client.get_or_create_collection("documents")
            uploaded_files = question["files"]
            question_text = question["text"]
            for file in uploaded_files:
                text = file.read().decode("utf-8")
                #highly customizable/ by chunks
                chunks = []
                chunk_size = 100
                overlap = 90
                step = chunk_size-overlap
                for i in range(0,len(text),step):
                    chunks.append(text[i:i+chunk_size])
                for i in range(len(chunks)):
                    chunks[i] = "Line "+str(i+1) + ": " + chunks[i]
                st.sidebar.write(len(chunks))
                tags = [str(i) for i in range(len(chunks))]
                collection.add(documents=chunks,ids=tags)
                with st.chat_message("system",avatar="🖥️"):
                    st.write("Files received!")
                curr["msg"].append({"role":"system", "avatar":"🖥️","content":"Files received!"})
            if (question_text.strip()):
                curr["msg"].append({"role":"user","content":question_text})
                curr["docs"].append({"role":"user","content":question_text})
                result = collection.query(query_texts = question_text,n_results = 10)
                for ans in result["documents"][0]:
                    curr["docs"].append({"role":"system","content":ans})
                with st.chat_message("user"):
                    st.write(question_text)
        #search for relevant information and add it to msg
        # msg.append({"role":"user","content":question})
            # search = .embed(model = "nomic-embed-text",input = st.session_state.documents)
            # ranking = cosine_similarity(ollama.embed(model = "nomic-embed-text",input = question)["embeddings"],search["embeddings"])[0]
            # rank_list =[]
            # top = ranking.argsort()[-3:]
            # for i in top:
            #     msg.append({"role":"system","content":st.session_state.documents[i]})
                response = groq_client.chat.completions.create(model = MODEL,messages = curr["docs"])
                curr["docs"].append({"role":"assistant","content":response.choices[0].message.content})
                curr["msg"].append({"role":"assistant","content":response.choices[0].message.content})
                with st.chat_message("assistant"):
                    st.write(response.choices[0].message.content)
        curr["busy"] = False
# for message in st.session_state.msg:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])