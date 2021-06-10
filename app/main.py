from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask_cors import CORS

from docx import Document
import pandas as pd
import mammoth

from app.util import read_docx_tables, unify_dfs
from app.utils.table_processor import TableProcessor, docx_to_csv

app = Flask(__name__)
CORS(app)


@app.route('/navigator/', methods=['POST', 'GET'])
@app.route('/temis/', methods=['POST', 'GET'])
def parse_document():
    format = request.form.get('format', False)
    uploaded_file = request.files['doc_file']

    if format:
        output_csv = 'res/output.csv'

        docx_to_csv(uploaded_file, output_csv)
        tp = TableProcessor(output_csv)

        response, _, _ = tp.process_tables()
    else:
        dfs = read_docx_tables(uploaded_file)
        response = [df.to_html(classes='data', header="true") for df in dfs]

    return (response.to_json(orient=format)) if format else jsonify(response)

@app.route('/tree/')
def tree():
    return render_template('tree.html', **locals())

@app.route('/', methods=['GET', 'POST'])
def index():
    style_map = """
        p[style-name='Section Title'] => h1:fresh
        p[style-name='Subsection Title'] => h2:fresh
    """
    response = 'No tables in the file'
    preview = ''
    if request.method == 'POST':
        uploaded_file = request.files['doc_file']

        preview = mammoth.convert_to_html(uploaded_file, style_map=style_map)
        preview = preview.value

        if Document(uploaded_file).tables:
            dfs = read_docx_tables(uploaded_file)
            dfs = unify_dfs(dfs)
            
            response = pd.concat(dfs, sort=False)
            response = [response.to_html(classes='data', header="true")]
    return render_template('index.html',  preview=preview, tables=response)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
