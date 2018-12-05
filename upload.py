from __future__ import print_function
import os, sys, json, re, requests
from flask import Flask, render_template, request

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
@app.route("/")
def index():
	"""Invoked when index route is accessed"""
	r_get = requests.get("http://127.0.0.1:5002/getdata")
	pdlf_data = r_get.json()
	return render_template("upload.html", message='',pdlf_data=pdlf_data)

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
			r = requests.post("http://127.0.0.1:5002/add", data= legal_doc_xml)
			r=r.json()
			r_get = requests.get("http://127.0.0.1:5002/getdata")
			pdlf_data = r_get.json()
			message = ''
			#Check if ths status from backend is OK
			if(r and r['STATUS'] == "OK"):
				message = "Succesfully Uploaded document "+"Plaintiff: "+r['plaintiff']+" Defendant: "+r['defendant']
			else:
				message = r['STATUS']
			return render_template("upload.html", message=message, pdlf_data=pdlf_data)
		else:
			return render_template("upload.html", message='Error!! Please provide valid file type, "xml" or "XML"', pdlf_data=pdlf_data); 

if __name__ == "__main__":
	app.run(port=4555, debug=True)
