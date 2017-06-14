import boto3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify,  make_response
import json

app = Flask(__name__)

def authenticate_user(username, password) :
    s3 = boto3.resource('s3')
    bucket_cred = s3.Bucket('YOURBUCKETNAME')
    is_authentic = 'false'
    for obj in bucket_cred.objects.all():
        key = obj.key
        print key
        if (key == 'TEXTFILEWITHCREDENTIALS') :
            a = json.loads(obj.get()['Body'].read())
            for it in a :
                if(it['username'] == username and it['password'] == password) :
                    is_authentic = 'true'
    return is_authentic

@app.route('/upload', methods=['POST'])
def upload_to_s3() :
    uname = request.form['uname']
    psswrd = request.form['psswrd']

    is_authentic = authenticate_user(uname, psswrd)
    if (uname == "" or psswrd == "") :
        return("Please authenticate user.")
    elif (is_authentic == 'true'):
        uploaded_files = {}
        file_from_page = request.files.getlist('file')
        files = []
        for it in file_from_page :
            files.append(it)

        s3_obj = boto3.resource('s3')
        for file_obj in files:
            file_it = open(file_obj.filename, 'w')
            file_it.write(file_obj.read())
            file_it.close()
            s3_obj.meta.client.upload_file(file_it.name, 'YOURBUCKETNAME', file_obj.filename)
            os.remove(file_it.name)
        return redirect('/')
    elif(is_authentic == 'false') :
        return ('User is not authenticated..')

@app.route('/', methods=['POST'])
def download_from_s3() :
    uname = request.form['uname']
    psswrd = request.form['psswrd']
    print uname
    print psswrd
    is_authentic = authenticate_user(uname, psswrd)
    if (uname == "" or psswrd == "") :
        return("Please authenticate user")
    elif(is_authentic == 'true'):
        request_from_page = request.form
        filename = [it for it in request_from_page][0]
        function_to_perform = filename.split('~~')[1]
        filename = filename.split('~~')[0]
        print function_to_perform
        print filename
        if (function_to_perform == 'Download') :
            s3_obj = boto3.resource('s3')
            filecontent=s3_obj.Object('YOURBUCKETNAME', filename).get()['Body'].read()#.decode('utf-8')
            response = make_response(filecontent)
            response.headers["Content-Disposition"] = "attachment; filename="+filename+";"
            return response
        elif(function_to_perform == 'Delete') :
            s3 = boto3.resource('s3')
            bucket = s3.Bucket('cc-6331-bucket')
            for obj in bucket.objects.all():
                if (obj.key == filename):
                    s3.Object(bucket.name, obj.key).delete()
        return redirect('/')
    elif(is_authentic == 'f'):
        return("User is not authenticated")

@app.route('/')
def index():
    uploaded_files = []
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('YOURBUCKETNAME')
    for obj in bucket.objects.all():
        key = obj.key
        body = obj.get()#['Body'].read()
        # print key
        uploaded_files.append(obj)

    return render_template('index.html', uploaded_files=uploaded_files)

if __name__ == "__main__":
	app.run(debug=True)
