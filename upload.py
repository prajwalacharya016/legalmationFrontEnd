from __future__ import print_function
import os, sys, json, re, requests
from flask import Flask, render_template, request
from requests.exceptions import ConnectionError

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
@app.route("/")
def index():
    """Invoked when index route is accessed"""
    message=''
    try:
        r_get = requests.get("http://127.0.0.1:5002/getdata", timeout=0.02)
        pdlf_data = r_get.json()
    except ConnectionError as e:
        pdlf_data = []
        message =  "No connection. Please check connection to api"
    return render_template("upload.html", message=message,pdlf_data=pdlf_data)

def readXML(filename):
    """
    Reads XML from file and returns a xml string

    Args:
        filename(str): Name of file to extract xml from

    Returns:
        xml string on success

    """
    with open(filename) as fd:
        legal_doc_xml = fd.read()
    return legal_doc_xml

@app.route("/upload", methods=["POST"])
def upload():
    """Invoked upload index route is accessed"""
    target = os.path.join(APP_ROOT, 'xml')
    FILE_TYPES = ["xml", "XML"]
    if not os.path.isdir(target):
        os.mkdir(target)
    for file in request.files.getlist("file"):
        filename=file.filename
        # Checks if valid file name
        if '.' in filename and filename.rsplit('.', 1)[1] in FILE_TYPES:
            destination = "/".join([target, filename])
            file.save(destination)
            legal_doc_xml = readXML(destination)
            pdlf_data=[]
            r={}
            message = ''
            try:
                r = requests.post("http://127.0.0.1:5002/add", data= legal_doc_xml)
                r=r.json()
                r_get = requests.get("http://127.0.0.1:5002/getdata", timeout=0.02)
                pdlf_data = r_get.json()
            except ConnectionError as e:
                print(e)
            #Check if ths status from backend is OK
            if(r and 'STATUS' in r and r['STATUS'] == "OK"):
                message = "Succesfully Uploaded document "+"Plaintiff: "+r['plaintiff']+" Defendant: "+r['defendant']
            elif(r and 'STATUS' in r) :
                message = r['STATUS']
            else:
                message="Unknown error occured,Check api connection and error console"
            return render_template("upload.html", message=message, pdlf_data=pdlf_data)
        else:
            return render_template("upload.html", message='Error!! Please provide valid file type, "xml" or "XML"', pdlf_data=pdlf_data);

if __name__ == "__main__":
    app.run(port=4555, debug=True)
