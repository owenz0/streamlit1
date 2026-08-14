import streamlit as st
st.set_page_config(layout = "wide")
if ("start_complete") not in st.session_state:
    with st.status("Starting Up...",expanded = True) as status:
        st.write("Initializing Environment (Up to 1min)")
        with (st.spinner()):
            import chromadb
            from groq import Groq
            from pathlib import Path
            from pypdf import PdfReader
            from streamlit_emoji_float import emoji_float
            if ("current_chat_id") not in st.session_state:
                st.session_state.current_chat_id = 1
            if ("chats") not in st.session_state:
                first_chat_id= 1
                st.session_state.chats = {
                    first_chat_id:{"busy":False,"title":"Conversation 1","msg":[{"role":"assistant","content":"Hello World!\nHow can I help you today?"}],"docs":[]}
                }
            if ("current_page") not in st.session_state:
                st.session_state.current_page = "home"
            if ("model") not in st.session_state:
                st.session_state.model = "Meta Llama 3.1"
            if ("easter_eggs") not in st.session_state:
                st.session_state.easter_eggs = False
            temp_client = chromadb.Client()
            temp_collection = temp_client.get_or_create_collection("Warmup")
            try:
                temp_collection.query(query_texts=["warmup"],n_results = 1)
                temp_client.delete_collection("Warmup")
            except Exception:
                pass
            status.update(label = "Environment Ready!",state="complete",expanded = False)
    st.session_state.start_complete = True
    st.rerun()
import chromadb
from groq import Groq
from pathlib import Path
from pypdf import PdfReader
from streamlit_emoji_float import emoji_float
# st.snow()
@st.cache_resource
def getGroq():
    API_KEY = st.secrets["GROQ_API_KEY"] #use only for streamlit
    return Groq(api_key = API_KEY)
@st.cache_resource
def getChroma():
    return chromadb.Client()
chroma_client = getChroma()
groq_client = getGroq()

top_left_col,main_header_col = st.columns([1,15],vertical_alignment = "center")
collection = chroma_client.get_or_create_collection(f"collection{st.session_state.current_chat_id}")

def deleteButton(indexToDelete):
    st.session_state.chats.pop(indexToDelete)
with main_header_col:
    st.title("CHATBOT!")
if st.button("🗑️ Clear Chat File History"):
    chroma_client.delete_collection(f"collection{st.session_state.current_chat_id}")
    st.rerun()
with top_left_col:
    with st.popover("☰",use_container_width=False):
        st.title("Settings")
        if (st.session_state.easter_eggs):
            easter_button = st.button("🐇🥚🐣",type = "primary")
        else:
            easter_button = st.button("🐇🥚🐣",type = "secondary")
        if (easter_button):
            st.session_state.easter_eggs = not st.session_state.easter_eggs
            st.rerun()
        st.session_state.model = st.selectbox("Choose a model: ",["Meta Llama 3.1","OpenAI OSS 20B","OpenAI OSS 120B"])

        if (st.button("Create new chat")):
            new_chat_id = max(st.session_state.chats.keys())+1
            st.session_state.chats[new_chat_id]= {"busy":False,"title":"Conversation "+str(new_chat_id),"msg":[{"role":"assistant","content":"Hello World!\nHow can I help you today?"}],"docs":[]}
            st.session_state.current_chat_id = new_chat_id
            st.rerun()
        st.write("Chat History")
        for chat_id,chat_data in list(st.session_state.chats.items()):
            col1,col2 = st.columns([5,3])
            is_active = chat_id == (st.session_state.current_chat_id)
            with col1:
                if (is_active):
                    button = st.button(f"{chat_data["title"]}",type = "primary",key = f"chat_{chat_id}",use_container_width=True)
                else:
                    button = st.button(f"{chat_data["title"]}",key=f"chat_{chat_id}",use_container_width=True)
            with col2: 
                delete_button = st.button(f"🗑️",key = f"del_{chat_id}",use_container_width=True)
            if delete_button and len(st.session_state.chats)>1:
                deleteButton(chat_id)
                st.session_state.current_chat_id = max(st.session_state.chats.keys())
                st.rerun()
            if button:
                st.session_state.current_chat_id = chat_id
                st.rerun()
if (st.session_state.easter_eggs):
    st.snow()
    emoji_float(emojis=["🔥", "🚀", "🎉","😄","🤩","🥳"],count = 50,minSize = 50,maxSize = 100,animationLength = 3,key = len(st.session_state.chats[st.session_state.current_chat_id]["docs"]))
model_call = {"Meta Llama 3.1":"llama-3.1-8b-instant","OpenAI OSS 20B":"openai/gpt-oss-20b","OpenAI OSS 120B":"openai/gpt-oss-120b"}
MODEL = model_call[st.session_state.model]
curr = st.session_state.chats[st.session_state.current_chat_id]   
for message in curr["msg"]:
    with st.chat_message(message["role"],avatar = message.get("avatar")):
        st.write(message["content"])
if not curr["busy"]:
    question = st.chat_input("Prompt: ",accept_file = "multiple",file_type=["txt","pdf"])
    if question:
        curr["busy"] = True
        if st.session_state.easter_eggs:
            st.balloons()
        with (st.spinner()):
            uploaded_files = question["files"]
            question_text = question["text"]
            for file in uploaded_files:
                file_extension = Path(file.name).suffix.lower()
                if (file_extension == ".txt"):
                    text = file.read().decode("utf-8")
                elif file_extension == ".pdf":
                    reader = PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text+=page.extract_text()+"\n"
                #highly customizable/ by chunks
                chunks = []
                chunk_size = 300
                overlap = 290
                step = chunk_size-overlap
                for i in range(0,len(text),step):
                    chunks.append(text[i:i+chunk_size])
                for i in range(len(chunks)):
                    chunks[i] = "Line "+str(i+1) + ": " + chunks[i]
                # for i,chunk in enumerate(chunks):
                #     print(i,len(chunk))
                tags = [file.name + str(i) for i in range(len(chunks))]
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
                    # st.write(len(ans))
                    # st.write(ans)
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