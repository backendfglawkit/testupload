from flask import Flask, render_template,redirect,url_for,request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField
from wtforms.validators import DataRequired
from flask_wtf import CSRFProtect
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import random
import string
from BunnyCDN.Storage import Storage
from BunnyCDN.CDN import CDN
import threading
import time
storage_api_key='859c94fa-7b78-4932-8d8642dc0823-ee19-4b09'
storage_zone_name='ccdstest'
storage_zone_region='SG'

obj_storage = Storage(storage_api_key,storage_zone_name,storage_zone_region)
obj_cdn = CDN('6e60323d-f8d4-40b8-adae-9e7cc10b5101ccda2a6f-ae96-4138-afda-8f8c66b74d73')

class UploadForm(FlaskForm):
    name = StringField('Enter the Name',validators=[DataRequired()])
    files = FileField('Files', validators=[DataRequired()], render_kw={"multiple": True})
    submit = SubmitField('Upload')

app = Flask(__name__)
csrf =CSRFProtect(app)
app.config['SECRET_KEY'] = 'asdasdsa'

el=[]
def task(pl):
    print("Started Task ...")
    print(threading.current_thread().name)
    time.sleep(0.1)
    try:
        obj_storage.PutFile(pl, storage_path=None)
        os.remove(pl)
        print("completed .....")
    except:
        el.append(pl)
    else:
        if pl in el:
            obj_storage.PutFile(pl, storage_path=None)
            os.remove(pl)
            el.remove(pl)
            print("completed .....")

    
@app.route('/', methods=["GET", "POST"])
def index():
    print((len(obj_storage.GetStoragedObjectsList('/product/asd'))))
    form = UploadForm()
    if form.validate_on_submit():
        folder_name = form.name.data
        folder_path = os.path.join('files', folder_name)
        os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
        files = request.files.getlist('files')  # Get list of uploaded files
        path = str('/product/' + folder_name)
        n = len(obj_storage.GetStoragedObjectsList(path))

        pl=[]
        for file in files:
            n += 1
            if file:
                original_filename = secure_filename(file.filename)
                file_extension = os.path.splitext(original_filename)[1]  # Extract file extension
                random_number = n  # Generate random number
                new_filename = f"{folder_name}-{random_number}{file_extension}"  # Append extension to filename
                file_path = os.path.join(folder_path, new_filename)  # Construct full file path
                file.save(file_path)  # Save the file
                pl.append(file_path)
                threading.Thread(target=task, args=(file_path,)).start()
                
        print(pl)
        pl=[]
        return redirect(url_for('index'))
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
 

# link- https://pypi.org/project/bunnycdnpython/