from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask_cors import CORS

import pandas as pd

from app.util import read_docx_tables, unify_dfs
from app.utils.table_processor import TableProcessor, docx_to_csv

app = Flask(__name__)
CORS(app)

@app.route('/tree/')
def analyse_document():
    return render_template('tree.html', **locals())


@app.route('/navigator/', methods=['POST', 'GET'])
@app.route('/temis/', methods=['POST', 'GET'])
def parse_document():
    format = request.form.get('format', False)
    uploaded_file = request.files['doc_file']
    output_csv = 'res/data/output.csv'
    docx_to_csv(uploaded_file, output_csv)
    # dfs = read_docx_tables(uploaded_file)
    tp = TableProcessor(output_csv)
    response, _, _ = tp.process_tables()

    # if format:
    #     dfs = unify_dfs(dfs)
    #     response = pd.concat(dfs, sort=False)
    #     response.reset_index(drop=True, inplace=True)
    # else:
    #     response = [df.to_html(classes='data', header="true") for df in dfs]

    return (response.to_json(orient=format)) if format else jsonify(response)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    response = ''
    if request.method == 'POST':
        uploaded_file = request.files['doc_file']
        dfs = read_docx_tables(uploaded_file)
        dfs = unify_dfs(dfs)
        
        response = pd.concat(dfs, sort=False)
        response = [response.to_html(classes='data', header="true")]
    return render_template('index.html',  tables=response)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
