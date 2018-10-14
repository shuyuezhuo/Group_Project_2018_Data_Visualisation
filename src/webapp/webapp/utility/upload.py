'''
**********************************************************************;
Project           : Visulisation of Massive-Scale Medical Image Datasets

Program name      : upload

Author            : Alexander Shiarella, Julianne Joswiak, Joseph Denis

Date last edited  : 2018/05/16

Purpose           : Images processing and performing demensional redution with full dataset.

Revision History  : 4.2

**********************************************************************;
'''


from webapp import app
import shutil
import os
from flask import flash

ALLOWED_EXTENSIONS = set(['png', 'jpeg', 'jpg'])
CSV_EXTENSION = set(['csv'])


def allowed_file(filename, criteria):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in criteria


# deletes and recreates empty directory
def clean(path):
    shutil.rmtree(path)
    os.mkdir(path)


# basic error checking (allowed extensions, filename exists)
def basic_check(file, error_object, extension, extension_global):
    if (file.filename == ''):
        flash(error_section + " required", category='danger')
        print("Did not upload any ", error_object)
        return False
    elif not (allowed_file(file.filename, extension_global)):
        flash("Wrong type of file for " + error_object \
              + ", please upload " + extension, category='danger')
        print("Uploaded invalid file in place of ", error_object)
        return False
    return True


# runs csv through basic error checking with CSV specific flashes
def check_csv(csv_file):
    print('Checking CSV...')
    if not basic_check(csv_file, 'CSV file', ' .csv file', CSV_EXTENSION):
        return False
    else:
        print('CSV file checking pass')
        print('--------------------')
        return True


#runs images through basic error checking,
#then cross-references them against the contents of the CSV file
def check_images(df, images, request):
    print('Start checking images reference...')
    images_count = len(images)
    csv_rows = df.shape[0]

    if images_count > csv_rows:
        flash('All images must be represented in CSV file', category='danger')
        print('CSV image reference error')
        return False

    for image in images:
        if not basic_check(image, 'image file(s)', '.png or .jpg files only for image set', ALLOWED_EXTENSIONS):
            return False
        elif not image.filename in df[df.columns[0]].values:
            flash('Image filename: ' + image.filename + ' not in CSV dataset', category='danger')
            print('CSV image reference error')
            return False
    print('Image checking pass')
    print('--------------------')
    return True
