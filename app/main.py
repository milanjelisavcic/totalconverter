from flask import Flask, request, jsonify
from flask import render_template, redirect, url_for

from app.util import read_docx_tables

app = Flask(__name__)

@app.route('/navigator/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"got name {name}")

    response = {}

    # Check if user sent a name at all
    if not name:
        response["ERROR"] = "no name found, please send a name."
    # Check if the user entered a number not a name
    elif str(name).isdigit():
        response["ERROR"] = "name can't be numeric."
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = f"Welcome {name} to our awesome platform!!"

    # Return the response in json format
    return jsonify(response)

@app.route('/navigator/', methods=['POST'])
def receive_docx():
    uploaded_file = request.files['file']
    dfs = read_docx_tables(uploaded_file)

    response = [df.to_json() for df in dfs]
    return jsonify(response)

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['doc_file']
    dfs = read_docx_tables(uploaded_file)
	
    # return redirect(url_for('index'))
    response = [df.to_html(classes='data', header="true") for df in dfs]
    return render_template('index.html',  tables=response)

@app.route('/')
def index():
    return render_template('index.html', **locals())

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
