from flask import Flask, request,render_template,send_file
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
from langchain.schema import Document 
from gtts import gTTS
import os

app = Flask(__name__)

folder_path = "db"

cached_llm = Ollama(model="llama3.2")

# embedding = FastEmbedEmbeddings()
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
)

raw_prompt = PromptTemplate.from_template(
    """ 
    <s>[INST] คุณเป็นผู้ช่วยทางเทคนิคที่มีความสามารถในการค้นหาเอกสาร ตอบลงท้ายด้วยค่ะ หรือ ฉัน หากคุณไม่มีข้อมูลที่เพียงพอในการตอบ โปรดแจ้งให้ทราบว่าไม่มีคำตอบจากข้อมูลที่ให้มา [/INST]</s>
    [INST] {input}
           บริบท: {context}
           คำตอบ:
    [/INST]
"""
)
def clean_text(text):
    # ลบเครื่องหมาย * ออกจากข้อความ
    return text.replace('*', '')

@app.route("/")
def index():
    return render_template("/index.html")

@app.route("/speak_answer", methods=["POST"])
def speak_answer():
    json_content = request.json
    answer = json_content.get("answer")
    
    cleaned_answer = clean_text(answer)
    # สร้างไฟล์เสียงใหม่หรือเขียนทับไฟล์เสียงเดิม
    tts = gTTS(text=cleaned_answer, lang='th')
    audio_file_path = "static/response.mp3"  # ใช้ชื่อไฟล์เดียวกัน
    tts.save(audio_file_path)
    
    # ส่ง URL กลับไป
    return {"audio_url": "/static/response.mp3"}

@app.route("/ai", methods=["POST"])
def aiPost():
    print("Post /ai called")
    json_content = request.json
    query = json_content.get("query")

    print(f"query: {query}")

    response = cached_llm.invoke(query)

    print(response)

    response_answer = {"answer": response}
    return response_answer


@app.route("/ask_pdf", methods=["POST"])
def askPDFPost():
    print("Post /ask_pdf called")
    json_content = request.json
    query = json_content.get("query")

    print(f"query: {query}")

    print("Loading vector store")
    vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)

    print("Creating chain")
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 20,
            "score_threshold": 0.1,
        },
    )

    document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
    chain = create_retrieval_chain(retriever, document_chain)

    result = chain.invoke({"input": query})

    print(result)

    sources = []
    for doc in result["context"]:
        sources.append(
            {"source": doc.metadata["source"], "page_content": doc.page_content}
        )

    response_answer = {
        "answer": result["answer"], 
        # "sources": sources
        }
    tts = gTTS(text=response_answer["answer"], lang='th')
    audio_file_path = "static/response.mp3"
    tts.save(audio_file_path)
    return response_answer


@app.route("/pdf", methods=["POST"])
def pdfPost():
    file = request.files["file"]
    file_name = file.filename
    file_extension = os.path.splitext(file_name)[1].lower()  # Get the file extension


    if file_extension == ".pdf":
        save_file = "pdf/" + file_name
        file.save(save_file)
        print(f"PDF filename: {file_name}")

        # Load and split PDF document
        loader = PDFPlumberLoader(save_file)
        docs = loader.load_and_split()
        print(f"docs len={len(docs)}")

    elif file_extension == ".txt":
        save_file = "txt/" + file_name
        file.save(save_file)
        print(f"TXT filename: {file_name}")

        # Load and wrap text document in a Document object
        with open(save_file, "r", encoding="utf-8") as f:
            text_content = f.read()

        # Wrap text in a Document object
        docs = [Document(page_content=text_content, metadata={"source": file_name})]
        print(f"docs len={len(docs)}")

    else:
        return {"status": "Unsupported file type"}, 400

    # Split documents into chunks
    chunks = text_splitter.split_documents(docs)
    print(f"chunks len={len(chunks)}")

    # Create vector store
    vector_store = Chroma.from_documents(
        documents=chunks, embedding=embedding, persist_directory=folder_path
    )
    vector_store.persist()

    response = {
        "status": "Successfully Uploaded",
        "filename": file_name,
        "doc_len": len(docs),
        "chunks": len(chunks),
    }
    return response

def start_app():
    # app.run(host="0.0.0.0", port=8080, debug=True)
    app.run(host="0.0.0.0", debug=False)


if __name__ == "__main__":
    start_app()
