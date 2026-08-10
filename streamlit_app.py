import streamlit as st
from groq import Groq
API_KEY = st.secrets["GROQ_API_KEY"] #use only for streamlit
model = st.selectbox("Choose a model: ",["Meta Llama 3.1","OpenAI OSS 20B","OpenAI OSS 120B"])
model_call = {"Meta Llama 3.1":"llama-3.1-8b-instant","OpenAI OSS 20B":"openai/gpt-oss-20b","OpenAI OSS 120B":"openai/gpt-oss-120b"}
MODEL = model_call[model]
client = Groq(api_key = API_KEY)
st.write("Hello World!")
if ("msg") not in st.session_state:
    st.session_state.msg = []
if ("busy") not in st.session_state:
    st.session_state.busy = False
st.title("CHATBOT!")
st.write((client.chat.completions.create(model = MODEL, messages = [{"role":"user","content":"hi"}])).choices[0].message.content)
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
# with st.form("calculator"):
#     num1 = st.number_input("First number")
#     num2 = st.number_input("Second number")
#     submitted = st.form_submit_button("add+ballons", disabled = st.session_state.busy)
#     if (submitted):
#         st.write(num1+num2)
#         # st.balloons()

if not st.session_state.busy:
    question = st.chat_input("Prompt: ")
    if question:
        st.session_state.busy = True
        st.balloons()
        st.write(question)
        with (st.spinner()):
            msg = []
        #search for relevant information and add it to msg
        # msg.append({"role":"user","content":question})
            # search = .embed(model = "nomic-embed-text",input = st.session_state.documents)
            # ranking = cosine_similarity(ollama.embed(model = "nomic-embed-text",input = question)["embeddings"],search["embeddings"])[0]
            # rank_list =[]
            # top = ranking.argsort()[-3:]
            # for i in top:
            #     msg.append({"role":"system","content":st.session_state.documents[i]})
            st.session_state.msg.append({"role":"user","content":question})
            response = client.chat.completions.create(model = MODEL,messages = st.session_state.msg)
            st.write("Answer: ", response.choices[0].message.content)
        st.session_state.busy = False


    
    # msg.append({"role":"assistant", "content": response["message"]["content"]})
    # documents.append(response["message"]["content"])
    # search = ollama.embed(model = "nomic-embed-text",input = documents)
    # print(*msg, sep = "\n")
