import datetime
import re
from copy import copy
from bs4 import BeautifulSoup
from flask import Flask, render_template, render_template_string, request, redirect, url_for
import os
from comparator import comparator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/rently/Downloads/new/'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    file1 = request.files['file1']
    file2 = request.files['file2']
    filename1 = file1.filename
    filename2 = file2.filename
    file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))

    html_template_soup = comparator(file1=os.path.join(app.config['UPLOAD_FOLDER'], filename1), file2=os.path.join(app.config['UPLOAD_FOLDER'], filename2))
    template_folder = "/home/rently/PycharmProjects/Brakeman Comparison/templates/"
    file_name = "Brakeman_comparison-" + datetime.datetime.now().strftime("%Y%m%d%H%M") + ".html"
    file_path = template_folder + file_name
    head, html_template_soup = html_template_soup.call_stack()
    content = str(html_template_soup).replace('{', '[').replace('}', ']')
    with open(file_path, "w") as html_template:
        html_template.write(head+content)
    print("REPORT NAME", file_name)
    return redirect(url_for('success', filename=file_name))


@app.route('/success')
def success():
    filename = request.args.get('filename')
    return render_template(filename)


if __name__ == '__main__':
    app.run(debug=True)
