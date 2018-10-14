'''
**********************************************************************;
Project           : Visulisation of Massive-Scale Medical Image Datasets

Program name      : views

Author            : Alexander Shiarella, Julianne Joswiak, Joseph Denis

Date last edited  : 2018/05/16

Purpose           : Support main flask application function call.

Revision History  : 4.1

**********************************************************************;
'''


from webapp import app
import pandas as pd
import os
import csv
from shutil import copyfile

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from werkzeug.utils import secure_filename

from webapp.utility.model import input_form
from webapp.utility.auth import auth
from webapp.utility.calculation import DataSet
from webapp.utility.calc_upload import DataSetUp
from webapp.utility.upload import allowed_file, clean, basic_check, check_csv, check_images

# imports for Bokeh and single file uploads
from bokeh.embed import server_document
from bokeh.client import pull_session

# other bokeh
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop

import time
import subprocess
import sys


# UPLOAD_FOLDER = '/vol/bitbucket/ajs3617/group/uploads'
CSV_UPLOAD_FOLDER = 'webapp/static/database/custom/data'
IMAGE_UPLOAD_FOLDER = 'webapp/static/database/custom/images'
CACHE_FOLDER = 'webapp/static/database/cache'
THUMBNAIL_UPLOAD_FOLDER = 'webapp/static/database/custom/thumbnails'

# NEEDED BY EXPORE PAGE
DEFAULT_IMG_PATH = '/static/database/default/images'
CUSTOM_IMG_PATH = '/static/database/custom/images'
CUSTOM_UPLOAD_PATH = 'webapp/static/database/custom/upload/images'

# CSV_FILENAME = 'default'
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
app.config['CSV_UPLOAD_FOLDER'] = CSV_UPLOAD_FOLDER
app.config['CACHE_FOLDER'] = CACHE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024


ALLOWED_EXTENSIONS = set(['png', 'jpg'])


@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        print('----------------------------------------')
        print('first method')
        clean(CSV_UPLOAD_FOLDER)
        clean(IMAGE_UPLOAD_FOLDER)
        clean(THUMBNAIL_UPLOAD_FOLDER)
        # request images and csv file via form in upload.html
        print('here4')
        images = request.files.getlist('images[]')
        print(images)
        print('here5')
        csv_file = request.files['file']
        print('--------------------')
        print('Cache CSV...')
        csv_file.save(os.path.join(app.config['CACHE_FOLDER'], 'image_data.csv'))
        print('CSV cached')
        print('--------------------')

        if 'file' not in request.files:
            flash('No file part', category='message')
            return redirect(request.url)

        # error checking on csv upload
        if not check_csv(csv_file):
            redirect(request.url)
        else:
            # turn csv into a dataframe, to be used for further processing
            df = pd.read_csv(app.config['CACHE_FOLDER'] + '/image_data.csv')

            # error checking on image uploads
            if not check_images(df, images, request):
                redirect(request.url)
            else:
                # delete and rebuild empty directories
                clean(CSV_UPLOAD_FOLDER)
                clean(IMAGE_UPLOAD_FOLDER)
                clean(THUMBNAIL_UPLOAD_FOLDER)

                # upload images into image upload folder
                for image in images:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
                print('Image uploaded')

                # move data from cache to data folder
                copyfile(app.config['CACHE_FOLDER'] + '/image_data.csv', \
                         app.config['CSV_UPLOAD_FOLDER'] + '/image_data.csv')
                # empty cache folder
                clean(CACHE_FOLDER)
                print('CSV uploaded')
                print('--------------------')
                path = os.path.join('webapp/static/database/custom/')
                run_calculations(path)

                return redirect(url_for('pick_data'))

    # empty cache folder
    clean(CACHE_FOLDER)
    return render_template('upload.html')


@app.route('/imagesupload', methods=['POST'])
@auth.login_required
def upload_files():
    if request.method == 'POST':
        print('----------------------------------------')
        print('second method')
        clean(CSV_UPLOAD_FOLDER)
        clean(IMAGE_UPLOAD_FOLDER)
        clean(THUMBNAIL_UPLOAD_FOLDER)
        # request images and csv file via form in upload.html
        print('here4')
        images = request.files.getlist('image')
        print(images)
        print('here5')
        csv_file = request.files['csv']
        print('--------------------')
        print('Cache CSV...')
        csv_file.save(os.path.join(app.config['CACHE_FOLDER'], 'image_data.csv'))
        print('CSV cached')
        print('--------------------')

        if 'csv' not in request.files:
            flash('No file part', category='message')
            return redirect(request.url)

        # error checking on csv upload
        if not check_csv(csv_file):
            redirect(request.url)
        else:
            # turn csv into a dataframe, to be used for further processing
            df = pd.read_csv(app.config['CACHE_FOLDER'] + '/image_data.csv')

            # error checking on image uploads
            if not check_images(df, images, request):
                redirect(request.url)
            else:
                # delete and rebuild empty directories
                clean(CSV_UPLOAD_FOLDER)
                clean(IMAGE_UPLOAD_FOLDER)
                clean(THUMBNAIL_UPLOAD_FOLDER)

                # upload images into image upload folder
                for image in images:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], filename))
                print('Image uploaded')

                # move data from cache to data folder
                copyfile(app.config['CACHE_FOLDER'] + '/image_data.csv', \
                         app.config['CSV_UPLOAD_FOLDER'] + '/image_data.csv')
                # empty cache folder
                clean(CACHE_FOLDER)
                print('CSV uploaded')
                print('--------------------')
                path = os.path.join('webapp/static/database/custom/')
                run_calculations(path)

                return redirect(url_for('pick_data'))

    # empty cache folder
    clean(CACHE_FOLDER)
    return render_template('upload.html')


#data exploration page - opens when a glyph is clicked on
@app.route('/explore/custom/<key>')
def explorer_custom(key):
    path = os.path.join(CUSTOM_IMG_PATH, key)
    return render_template("explore.html", img_path=path, key=key, template="Flask")


# data exploration page - opens when a glyph is clicked on
@app.route('/explore/default/<key>')
def explorer_default(key):
    path = os.path.join(DEFAULT_IMG_PATH, key)
    return render_template("explore.html", img_path=path, key=key, template="Flask")


# data exploration page - opens when a glyph is clicked on
@app.route('/explore/full/<key>')
def explorer_full(key):
    path = os.path.join(FULL_IMG_PATH, key)
    return render_template("explore.html", img_path=path, template="Flask")





# helper function for filetype validation
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Bokeh visualization page with single file upload
@app.route('/viz', methods=['GET', 'POST'])
def visualization():
    clean('webapp/static/database/custom/upload/data')
    clean('webapp/static/database/custom/upload/images')
    clean('webapp/static/database/custom/upload/thumbnails')

    print('--------------------')
    # s = request.args['s'] # for testing input from first page
    choice = request.args['s']

    if choice == "default":
        # get Bokeh server documment to run visualization BokehJS script
        script = server_document("http://localhost:5003/bokehapp_default")

    elif choice == "custom":
        script = server_document("http://localhost:5005/bokehapp_custom")

    elif choice == "full":
        script = server_document("http://localhost:5008/bokehapp_full")

    # from official Flask example
    if request.method == 'POST':
        # check for file in POST
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # no file selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # file selected allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('webapp/static/database/custom/upload/images', "USER_UPLOAD.png"))
            print("Runing dimention reduction on single image...")
            path = os.path.join('webapp/static/database/custom/upload')
            upload_set = DataSetUp(img_direc=path, name='custom/upload')
            upload_set.preProcessImage()
            upload_set.run()
            print("Dimention reduction finish")
            print('--------------------')
    return render_template("embed.html", script=script, template="Flask")


def run_calculations(path):
    print("Start processing images...")
    testDS = DataSet(img_direc=path, name='custom')
    testDS.preProcessImage()
    testDS.dimenReduceImage()
    print("Finish processing images")
    print('--------------------')



# opens new page with uploaded image
@app.route('/', methods=['GET', 'POST'])
def pick_data():
    form = input_form(request.form)
    if request.method == 'POST':

        choice = request.form['button']
        # s = 1
        if choice == 'default':
            return redirect(url_for('visualization', s=choice))

        if choice == 'custom':
            return redirect(url_for('visualization', s=choice))

        if choice == 'full':
            return redirect(url_for('visualization', s=choice))

        if choice == 'upload':
            return redirect(url_for('upload_page', s=choice))
    else:
        s = None

    return render_template('index.html', form=form, s=5)


app.secret_key = 'n\xb6\xe4\x8a7g.\xac&\xa8\xea\x8da\x12\xc2\xd1ZU\xb0\x88V\xd9Q\x9f'

if __name__ == '__main__':
    app.run(debug=True)
