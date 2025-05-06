import os
import glob
from flask import Flask, request, jsonify, render_template
from langchain_community.document_loaders import WebBaseLoader, DirectoryLoader, TextLoader, UnstructuredXMLLoader, PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.history_aware_retriever import create_history_aware_retriever
import re

os.environ["OPENAI_API_KEY"] = "********"

app = Flask(__name__)

def get_documents_from_sources(sources):
    all_docs = []
    split_docs = []

    for source in sources:
        if source.startswith('http'):
            loader = WebBaseLoader(source)
            docs = loader.load()
            all_docs.extend(docs)

        elif source.endswith('data'):
            loader = DirectoryLoader(source, glob="**/*.txt", loader_cls=TextLoader)
            docs = loader.load()
            all_docs.extend(docs)
        
        elif os.path.isdir(source):
            xml_files = glob.glob(os.path.join(source, "*.xml"))
            if xml_files:
                for xml_file in xml_files:
                    try:
                        docs = load_xml_data(xml_file)
                        all_docs.extend(docs)
                    except Exception as e:
                        print(f"Error loading {xml_file}: {str(e)}")
            
            else:
                loader = DirectoryLoader(source, glob="**/*.pdf", loader_cls=PyPDFLoader)
                docs = loader.load()
                all_docs.extend(docs)

    splitter = RecursiveCharacterTextSplitter(
                chunk_size=200000,
                chunk_overlap=500
            )
    split_docs = splitter.split_documents(all_docs)
        
    return split_docs

def load_xml_data(xml_file):
    loader = UnstructuredXMLLoader(xml_file)
    docs = loader.load()
    return docs

def create_db(docs):
    embedding = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorStore = FAISS.from_documents(docs, embedding=embedding)
    return vectorStore

def create_chain(vectorStore):
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Anda adalah Chatbot AI yang membantu. Nama mu adalah BMKG-GPT."),
        ("system", "BMKG-GPT adalah Chatbot AI yang membantu memberikan informasi dalam bidang Meteorologi Klimatologi dan Geofisika yang dimiliki oleh BMKG, BMKG-GPT adalah Milik DTA BMKG."),
        ("system", "Jawab pertanyaan user berdasarkan context: {context}"),
        ("system", "Jawab pertanyaan informasi gempa bumi dengan menanyakan kembali data gempa bumi apa yang dibutuhkan, Gempa Bumi Terbaru?, Gempa Bumi Dengan Kekuatan Lebih dari 5 (M>5)? , Gempa Bumi Dirasakan, atau Gempa bumi Berpotensi TSUNAMI ?"),
        ("system", "Setelah memberikan jawaban informasi gempa bumi berikan saran dari bmkg dan antisipasi gempa bumi"),
        ("system", "Berikan informasi gempa bumi atau data gempa bumi dari database sources atau database pribadi yang telah diberikan"),
        ("system", "Jika user menanyakan informasi cuaca tanyakan informasi cuaca apa yang dibutuhkan, BMKG-gpt menyediakan informasi Prakiraan Cuaca harian dan Prakiraan Cuaca bandara, Tanyakan spesifikasi Kota atau Bandara?"),
        ("system", "Jawab informasi Prakiraan Cuaca harian di tambah berikan link ini (https://cuaca.bmkg.go.id/dwt/), Untuk Informasi Cuaca Bandara tambahkan link ini (https://web-aviation.bmkg.go.id/web/observation.php)"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])



    chain = create_stuff_documents_chain(
        llm=model,
        prompt=prompt
    )

    retriever = vectorStore.as_retriever(search_kwargs={"k": 3})

    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=retriever,
        prompt=retriever_prompt
    )

    retriever_chain = create_retrieval_chain(
        history_aware_retriever,
        chain
    )

    return retriever_chain

def process_chat(chain, question, chat_history):
    response = chain.invoke({
        "input": question,
        "chat_history": chat_history
    })

    answer = response.get("answer", "")

    answer = re.sub(r'[#*]+', '', answer)

    return answer

sources = [
    'https://id.wikipedia.org/wiki/Badan_Meteorologi,_Klimatologi,_dan_Geofisika',
    'https://id.wikipedia.org/wiki/Sekolah_Tinggi_Meteorologi,_Klimatologi,_dan_Geofisika',
    'https://id.wikipedia.org/wiki/Geofisika',
    'https://id.wikipedia.org/wiki/Klimatologi',
    'https://id.wikipedia.org/wiki/Meteorologi',
    r'D:\BMKG-GPT\data',
    r'D:\BMKG-GPT\pdf',  
    r'D:\BMKG-GPT\xmldata' 
]

docs = get_documents_from_sources(sources)
vectorStore = create_db(docs)
chain = create_chain(vectorStore)

chat_history = []


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_question', methods=['POST'])
def process_question():
    data = request.get_json()
    question = data['question']

    response = process_chat(chain, question, chat_history)
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=response))

    return jsonify({'response': response})

def load_xml_data(xml_file):
    loader = UnstructuredXMLLoader(xml_file)
    docs = loader.load()
    return docs



if __name__ == '__main__':

    app.run(debug=True)

