import datetime
import re
import time
from copy import copy
from bs4 import BeautifulSoup
from flask import Flask, render_template, render_template_string, request, redirect, url_for
import os
from brakeman_comparator import Comparator

app = Flask(__name__, template_folder="/home/rently/PycharmProjects/Brakeman-Comparison/templates/")
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
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
    file1_before_deployment = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
    file2_after_deployment = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

    template_folder = "/home/rently/PycharmProjects/Brakeman-Comparison/templates/"
    print("File 1 Name: {}\nFile 2 Name: {}".format(file1_before_deployment, file2_after_deployment))

    Obj = Comparator(file1_before_deployment, file2_after_deployment)
    head, html_template_soup = Obj.call_stack()

    file1_before_deployment = file1_before_deployment.split("/")[-1]
    file2_after_deployment = file2_after_deployment.split("/")[-1]
    file_name = "compared_" + file2_after_deployment.split(".html")[0] + "_with_" + file1_before_deployment.split(".html")[0] + ".html"
    file = template_folder + file_name
    content = str(html_template_soup).replace('{', '[').replace('}', ']')
    with open(file, "w") as html_template:
        html_template.write(head + content)
    print("REPORT NAME", file_name)
    return redirect(url_for('success', filename=file_name))


@app.route('/success')
def success():
    filename = request.args.get('filename')
    return render_template(filename)


if __name__ == '__main__':
    app.run(debug=True)
