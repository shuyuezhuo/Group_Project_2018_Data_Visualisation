# Group_Project_2018
# Visualisation of Massive-Scale Medical Image Datasets Using the DSI Data Observatory  
| Final Report|  
Joseph Denis, Ghadeer Emara, Julianne Joswiak, Alexander Shiarella, Shengwei Zhang, Shuyue Zhuo  
fjd810, gae17, jj2816, ajs3617, sz8816, sz8216g@doc.ic.ac.uk  
Supervisor: Professor Daniel Rueckert  
Module: CO530, Imperial College London  


### 1 Introduction

Dimensionality reduction is a powerful tool for exploratory data analysis and visualisation, com-
monly used to understand the high-dimensional variability of image datasets. While two-dimensional
representations can be useful in interpreting image similarity, interactive data visualisation would
greatly improve on the utility of these traditionally static plots. Moreover, if dimensionality reduction
algorithms were abstracted into a dynamic user interface, it could offer a novel analysis tool to users
unfamiliar with machine learning.

### 2 Purpose and Usage

In this project, we aimed to provide an interactive visualisation plot where many thousands of
images of a certain type (e.g. X-rays of lung images) could be collected and grouped together using a
dedicated machine learning algorithm. The overall purpose of the algorithm is to employ dimension-
ality reduction techniques such as Principal Component Analysis (PCA), Locally Linear Embedding
(LLE), Multidimensional Scaling (MDS) or Isomap such that these images of large sizes could be read,
processed and placed on the plot within a reasonable period of time.
The algorithm intends to gauge similarities between the images and perform an appropriate clustering
such that the user, a medical professional or otherwise, could then easily and interactively explore the
plot to identify patterns and gain further insight into the data. We also intended to create a fully
functioning and truly interactive plot by incorporating useful features such as zooming into a certain
section, cropping a subsection for deeper analysis, viewing data associated with each image, images
appearing on hover-over, and switching between the various machine learning algorithms with ease.
Our larger goals ultimately included reasonably fast processing times, such as when allowing the user
to upload their own data-set, and then additionally when allowing them to upload individual images
which would be computed and added to the plot amongst the other, pre-computed images.
By completing this project, we hoped to provide both a new method for understanding and diagnosing
disease, and a case study on the scalability of machine learning web applications for image dataset
analysis.

### 3 Application download/serving instructions

Prerequisites:
Unix or Linux computer with pip, Python3, virtualenv, and web browser (ideally Google Chrome) installed.  

**Version 1:**
  Note: if necessary to complete the steps below, kill any processes on ports 5003 and 5005
  
  1. Unzip project.zip
  2. In 3 separate terminal windows cd ./project
  3. In terminal window 1  
    a .chmod 755 install env.sh  
    b. source ./install env.sh  
    c. chmod 755 runFlask.sh  
    d. source ./runFlask.sh  
  4. in browser, go to: http://127.0.0.1:5000/  
  5. In terminal window 2:  
    a. chmod 755 bokehDefault.sh  
    b. source ./bokehDefault.sh  
  6. In terminal window 3:  
    a. chmod 755 bokehCustom.sh  
    b. source ./bokehCustom.sh  
    
**Version 2 (if there is an issue with the bash scripts)**
  
Note: if necessary to complete the steps below, kill any processes on ports 5003 and 5005 (or update  
the numbers below to use free ports).  

  1. Unzip project.zip  
  2. In 3 separate terminal windows cd ./project  
  
  From terminal window 1:  
    1. Create a virtual environment in a chosen directory by running command: virtualenv appenv  
    2. Activate virtual environment by running command directory containing appenv: source ./appenv/bin/activate  
    3. Unzip our included file set in a chosen directory  
    4. From the top of this file set (the same directory as requirements.txt) run command: pip install -r requirements.txt  
    5. cd webapp (you should now be in the directory webapp, containing the subdirectory webapp)  
    6. pip install -editable .  
    7. export FLASK APP=webapp  
    8. export FLASK DEBUG=true  
    9. flask run  
    10.in browser, go to: http://127.0.0.1:5000/  
    
  From terminal window 2:  
    1. activate appenv  
    2. Go to src/webapp/webapp/directory  
    3. Run command: bokeh serve -port 5003 -allow-websocket-origin=127.0.0.1:5000 bokehapp default  
    
  From terminal window 3:  
    1. activate appenv  
    2. Go to src/webapp/webapp  
    3. Run command: bokeh serve -port 5005 -allow-websocket-origin=127.0.0.1:5000 bokehapp custom  
    
We included a small dataset for the default, and disconnected the full dataset directory interface. The
default can now be accessed in the browser by clicking the lung dataset button.
To test our data upload tool, use the files in the included folder test upload (in the top directory of
the unzipped file set). The uploaded images can be viewed by clicking the custom dataset button on
the home page.

To test the single file upload prototype, you can use any of the additional images in the test single
folder or those in the test upload folder (for a repeat upload).
Note: Currently the download csv feature is only a rough prototype - it needs to be adapted to remove
hard coding the download only filtered table displayed.
