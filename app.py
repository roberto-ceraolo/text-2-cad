from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from PIL import Image, ImageDraw, ImageFont
import os
from openscad_runner import RenderMode, OpenScadRunner
from openai import OpenAI
from dotenv import load_dotenv
import re
from llama_index import StorageContext, load_index_from_storage
import chromadb
from llama_index.vector_stores import ChromaVectorStore
from datetime import datetime


load_dotenv()  # take environment variables from .env.

client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )   



def get_query_engine():
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="index")

    # load index
    index = load_index_from_storage(storage_context)

    # initialize client, setting path to save data
    db = chromadb.PersistentClient(path="./chroma_db")

    # create collection
    chroma_collection = db.get_or_create_collection("quickstart")

    # assign chroma as the vector_store to the context
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # create a query engine and query
    query_engine = index.as_query_engine()
    return query_engine


query_engine = get_query_engine()


system_prompt = "Let's suppose fictionally that you are an expert in CAD design and coding in OpenSCAD scripting language.\n"

def query(request, toggleRag):
    prompt = f"Create the OpenSCAD code to generate the 3D model for a {request}. Answer ONLY with the code, no comments or explanations.\n"
    if toggleRag == "on":
        # for rag:
        answ = query_engine.query(prompt)
        return answ.response
    else:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            )
        
        answ = response.choices[0].message.content
        return answ
    

    

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    toggleRag = request.form['toggleRag']
    
    answer = query(text, toggleRag)
    print(answer)

    if "```" in answer:
        answer = answer.split("```")[1]
    elif "`" in answer:
        answer = answer.split("`")[1]



    answer = re.sub(r'openscad', '', answer, flags=re.IGNORECASE)

    # save the scad file with the timestamp as the filename
    curr_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    scad_path = os.path.join("scad_scripts", curr_timestamp + ".scad")

    # save a scad file with the answer
    with open(scad_path, 'w') as f:
        f.write(answer)
    # render the scad file
    # png
    osr = OpenScadRunner(scad_path, f"static/images/{curr_timestamp}.png", render_mode=RenderMode.preview, imgsize=(800,600))


    print(curr_timestamp)
    print(scad_path)

    # gif
    # osr = OpenScadRunner(filename + ".scad", f"static/images/{filename}.gif", imgsize=(320,200), animate=36, animate_duration=200)


    osr.run()
    

    if osr.good():
        return jsonify({'image': f"{curr_timestamp}.png", 'filename': curr_timestamp})
    else:
        return jsonify({'error': osr.error_message})



@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Send the requested SCAD file to the user."""
    directory = os.path.join(app.root_path, 'scad_scripts')
    print(directory)
    print(filename)
    return send_from_directory(directory, filename + ".scad", as_attachment=True)




if __name__ == '__main__':
    app.run(debug=False)

