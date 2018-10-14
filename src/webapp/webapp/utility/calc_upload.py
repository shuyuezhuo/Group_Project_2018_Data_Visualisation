'''
**********************************************************************;
Project           : Visulisation of Massive-Scale Medical Image Datasets

Program name      : calc_upload

Author            : Alexander Shiarella, Shuyue Zhuo

Date last edited  : 2018/05/16

Purpose           : Single image processing and performing demensional redution with full dataset.

Revision History  : 3.1

Description       : The program is divided into two functions, preProcessImage() and run().

                    The preProcessImage() function will read all the images specified in the CSV file. It will
                    saves thumbnails to 'thumbnail' folder and saves two pkl files, dataFrame.pkl and downsampledImage.pkl,
                    where the first contains image names and thumbnail path and the second contains downsampled images.
                    This function will require readImage(dataFrame).

**********************************************************************;
'''
import numpy as np
import pandas as pd
import pickle
import glob
import sys
import os
from PIL import Image
from sklearn import decomposition
from sklearn import manifold
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Panel, Tabs




parent_path = os.path.join('webapp/static/database/custom')

class DataSetUp:

    MAX_H = 100
    MAX_W = 100

    def __init__(self, img_direc, name):
        self.DIRECTORY = img_direc
        self.IMGS = [] # array to hold image filenames
        self.IMGS_T = [] # array to hold thumbnail filenames
        self.DATAFRAME = os.path.join(self.DIRECTORY, 'data', 'dataFrame_upload.pkl')
        self.name = name

##############################################################################################################
# preprocess image
##############################################################################################################

    def readImage(self, dataFrame):

        #make sure the image names are stored in the 'Image Index' column in the csv
        counter = len(dataFrame['Image Index'])
        imageStack = np.zeros(counter * self.MAX_H * self.MAX_W, dtype='int16').reshape(counter, self.MAX_H * self.MAX_W)
        counter = 0
        print('Reading single image...')
        for imgName in dataFrame['Image Index']:  # All png images

            imgFile = Image.open(os.path.join(self.DIRECTORY, 'images', imgName)).convert('L')# todo:IMAGE_DIRECTORY

            # Add filename to IMGS array
            self.IMGS.append(imgName)

            imgFile.thumbnail((self.MAX_W, self.MAX_H))

            # Save thumbnail TODO changed to static
            thumbnailPath = os.path.join(self.DIRECTORY, 'thumbnails', imgName)# todo:'thumbnail', change to where can save thumbnail
            imgFile.save(thumbnailPath)

            thumbnailBokehPath = os.path.join('static', 'database', self.name, 'thumbnails', imgName)

            # thumbnailBokehPath = os.path.join('static', 'thumbnail', imgName)

            # Add filename to IMGS_T array
            self.IMGS_T.append(thumbnailBokehPath)

            imageData = np.array(imgFile, dtype='int16')
            imageStack[counter] = imageData.reshape(1, imageData.size)
            imgFile.close()
            counter += 1
            
        print('Finish reading image')
        dataFrame['imgs'] = self.IMGS
        dataFrame['thumbs'] = self.IMGS_T

        packDataFrameAndImages = {'frame': dataFrame, 'images': imageStack}

        return packDataFrameAndImages



    def preProcessImage(self):
        # read CSV file
        upload_data = {'Image Index' : 'USER_UPLOAD.png'}
        dataFrame = pd.DataFrame(data = upload_data, index={0})
        
        # save thumbnails
        diction = self.readImage(dataFrame)

        # Pickle the downsampled image
        output = open(os.path.join(self.DIRECTORY, 'data', 'downsampledImage.pkl'), 'wb')
        pickle.dump(diction['images'], output)

        # Pickle the dataframe
        output = open(os.path.join(self.DIRECTORY, 'data','dataFrame.pkl'), 'wb')
        pickle.dump(diction['frame'], output)



################################################################################################################
# dimension reduction
################################################################################################################
    def PCA(self, imageStack):
        pca = decomposition.PCA(n_components=2)
        pca.fit(imageStack)
        return pca.transform(imageStack)

    def LLE(self, imageStack, n_neighbors, n_components):
        lle = manifold.LocallyLinearEmbedding(n_neighbors, n_components, eigen_solver='auto', method='standard')
        y = lle.fit_transform(imageStack)
        return y

    def IOSMAP(self, imageStack, n_neighbors, n_components):
        return manifold.Isomap(n_neighbors, n_components).fit_transform(imageStack)

    def MDS(self, imageStack, n_components):
        mds = manifold.MDS(n_components, max_iter=100, n_init=1)
        y = mds.fit_transform(imageStack)
        return y



    def run(self):    
        
        # read pre-processed file
        pkl_file1 = open(os.path.join(parent_path, 'data', 'downsampledImage.pkl'), 'rb')
        image1 = pickle.load(pkl_file1)
        
        pkl_file2 = open(os.path.join(self.DIRECTORY, 'data', 'downsampledImage.pkl'), 'rb')
        image2 = pickle.load(pkl_file2)

        image = np.append(image1, image2, axis=0)

        # read dataframe file
        pkl_file1 = open(os.path.join(parent_path, 'data', 'dataFrame.pkl'), 'rb')
        dataFrame1 = pickle.load(pkl_file1)
        pkl_file2 = open(os.path.join(self.DIRECTORY, 'data', 'dataFrame.pkl'), 'rb')
        dataFrame2 = pickle.load(pkl_file2)

        dataFrame = dataFrame1.append(dataFrame2)

        # perform dimention reduction
        pca_data = self.PCA(image)

        lle_data = self.LLE(image, 10, 2)

        iosmap_data = self.IOSMAP(image, 10, 2)

        mds_data = self.MDS(image, 2)

        # add extra information
        dataFrame['PCA_X'] = pca_data[:, 0]
        dataFrame['PCA_Y'] = pca_data[:, 1]

        dataFrame['LLE_X'] = lle_data[:, 0]
        dataFrame['LLE_Y'] = lle_data[:, 1]

        dataFrame['ISOMAP_X'] = iosmap_data[:, 0]
        dataFrame['ISOMAP_Y'] = iosmap_data[:, 1]

        dataFrame['MDS_X'] = mds_data[:, 0]
        dataFrame['MDS_Y'] = mds_data[:, 1]

        # Pickle the dataframe
        output = open(self.DATAFRAME, 'wb')
        pickle.dump(dataFrame, output)