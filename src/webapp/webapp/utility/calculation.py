'''
**********************************************************************;
Project           : Visulisation of Massive-Scale Medical Image Datasets

Program name      : calculation

Author            : Shuyue Zhuo

Date last edited  : 2018/05/11

Purpose           : Images processing and performing demensional redution with full dataset.

Revision History  : 2.3

Description       : The program is divided into two functions, preProcessImage() and dimenReduceImage().

                    The preProcessImage() function will read all the images specified in the CSV file. It will
                    save thumbnails to 'thumbnail' folder and save two pkl files, dataFrame.pkl and downsampledImage.pkl,
                    where the first contains image names and thumbnail path and the second contains downsampled images.
                    This function will require readImage(dataFrame)

                    The dimenReduceImage() gets the downsampled image from downsampledImage.pkl and then performs dimension reduction
                    (including PCA, LLE, ISOMAP, MDS). After that, it adds the additional columns to the dataFrame.pkl, which should
                    be read by front-end.
                    This function will require PCA(), LLE(), ISOMAP() and MDS()

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


class DataSet:

    MAX_H = 100
    MAX_W = 100

    def __init__(self, img_direc, name):
        self.DIRECTORY = img_direc
        self.IMGS = [] # array to hold image filenames
        self.IMGS_T = [] # array to hold thumbnail filenames
        self.CSV_FILE = os.path.join(self.DIRECTORY, 'data', 'image_data.csv')
        self.DATAFRAME = os.path.join(self.DIRECTORY, 'data', 'dataFrame.pkl')
        self.name = name

##############################################################################################################
# preprocess image
##############################################################################################################

    def readImage(self, dataFrame):

        #make sure the image names are stored in the 'Image Index' column in the csv
        counter = len(dataFrame['Image Index'])
        imageStack = np.zeros(counter * self.MAX_H * self.MAX_W, dtype='int16').reshape(counter, self.MAX_H * self.MAX_W)
        counter = 0
        print("Processing image files...")
        for imgName in dataFrame['Image Index']:  # All png images

            imgFile = Image.open(os.path.join(self.DIRECTORY, 'images', imgName)).convert('L')# todo:IMAGE_DIRECTORY

            # print out image filename in commandline (for testing)
            

            # Add filename to IMGS array
            self.IMGS.append(imgName)

            imgFile.thumbnail((self.MAX_W, self.MAX_H))

            # Save thumbnail
            thumbnailPath = os.path.join(self.DIRECTORY, 'thumbnails', imgName)
            imgFile.save(thumbnailPath)

            thumbnailBokehPath = os.path.join('static', 'database', self.name, 'thumbnails', imgName)

            # Add filename to IMGS_T array
            self.IMGS_T.append(thumbnailBokehPath)

            imageData = np.array(imgFile, dtype='int16')
            imageStack[counter] = imageData.reshape(1, imageData.size)
            imgFile.close()
            counter += 1
            
        print("Finish processing image files")
        dataFrame['imgs'] = self.IMGS
        dataFrame['thumbs'] = self.IMGS_T

        packDataFrameAndImages = {'frame': dataFrame, 'images': imageStack}

        return packDataFrameAndImages



    def preProcessImage(self):
        # read CSV file
        dataFrame = pd.DataFrame.from_csv(self.CSV_FILE, index_col=None)#todo: CSV_FILE, now is constant
        dataFrame.rename(columns={ dataFrame.columns[0]: "Image Index" })

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



    def dimenReduceImage(self):
        # read pre-processed file
        print('Start dimension reduction...')
        print('This may take a while, for 5000 images typical processing time is 20 mins')
        pkl_file = open(os.path.join(self.DIRECTORY, 'data', 'downsampledImage.pkl'), 'rb')
        image = pickle.load(pkl_file)

        # read dataframe file
        pkl_file = open(os.path.join(self.DIRECTORY, 'data', 'dataFrame.pkl'), 'rb')
        dataFrame = pickle.load(pkl_file)
        print
        # perform dimention reduction
        print('Running PCA algorithm...')
        pca_data = self.PCA(image)
        print('Running LLE algorithm...')
        lle_data = self.LLE(image, 10, 2) # switch to 10
        print('Running ISOMAP algorithm...')
        iosmap_data = self.IOSMAP(image, 10, 2) # switch to 10
        print('Running MDS algorithm...')
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
        
        print('Finish dimension reduction')



