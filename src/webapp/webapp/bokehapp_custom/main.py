'''
**********************************************************************;
Project           : Visulisation of Massive-Scale Medical Image Datasets

Program name      : main

Author            : Alexander Shiarella

Date last edited  : 2018/05/10

Purpose           : Bokeh function that serves the user interface.
                    Designed for custom dataset.

Revision History  : 4.0

**********************************************************************;
'''

# bokeh serve --port 5005 --allow-websocket-origin=127.0.0.1:5000 bokehapp_custom

import numpy as np
import pandas as pd
import glob
import sys
import os
from PIL import Image
from sklearn import decomposition
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import ColumnDataSource, HoverTool, Select, CDSView, BooleanFilter, GroupFilter, IndexFilter, TapTool, OpenURL, PolySelectTool, LassoSelectTool
from bokeh.models.widgets import Panel, Tabs, CheckboxGroup, MultiSelect, Toggle, DataTable, TableColumn
from bokeh.models.mappers import CategoricalColorMapper
from bokeh.layouts import row, column, widgetbox, layout
from bokeh.palettes import Spectral5, Colorblind8

from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from os.path import dirname, join


FILE_PATH = 'static/database/custom/data/dataFrame.pkl'
if (os.path.exists('static/database/custom/upload/data/dataFrame_upload.pkl')):
    FILE_PATH = 'static/database/custom/upload/data/dataFrame_upload.pkl'
print(FILE_PATH)
COLORS = Colorblind8
COUNTABLE_LIMIT = 5 # max number of unique values in a category to be "countable"
X_INIT = 'PCA_X' # name of column for initial x-axis
Y_INIT = 'PCA_Y' # name of column for initial y-axis
COLOR_INIT = 'Patient Gender' # name of column for initial coloring
TOGGLE_INIT = False # set to True to init with image glyph view, False for mouseover view
PLOT_TITLE = 'X-Plore Image Database Tool'
THUMBS = 'thumbs' # column name with thumbnail file paths

TYPE = 'custom'

# function that returns an interavtive plot
def visualise():

    # plot for mouse over view - "Images" button is off
    if toggle_val == False:

        # mouseover tool containing image and attribute
        hover = HoverTool( tooltips="""
        <div>
            <div>
                <img
                    src="@thumbs" alt="thumbs"
                    style="float: left; marsquaregin: 0px 50px 15px 0px;"
                    border="2"
                ></img>
            </div>
            <div>
                <span style="font-size: 12px; color: #966;">Index: $index</span>
            </div>
            <div>
                <span style="font-size: 12px; font-weight: bold;">@{imgs}</span>
            </div>
            <div>
                <span style="font-size: 12px; font-weight: bold;">ID: @{Patient ID}</span>
            </div>
        </div>
        """
        )

        # create figure with mouse over, lasso, tap, pan, and zoom tools
        tools = [hover, 'box_zoom', 'pan', 'zoom_out', 'zoom_in', 'reset', 'tap', lasso]
        p = figure(logo=None, tools=tools, title=PLOT_TITLE)

        # only run lasso tool callback after loop drawn
        p.select(LassoSelectTool).select_every_mousemove = False


        # map color based on col_cat selected
        cat_set = list(set(source.data[color_cat])) # group by value
        mapper = CategoricalColorMapper(palette=COLORS, factors=cat_set)

        # add circle plot with selected values
        p.circle(x=x_axis, y=y_axis, size=5, source=source, color={'field': color_cat, 'transform': mapper})

        # if plot selection changex, run selection_callback() to update table
        source.on_change('selected', selection_callback)

    # plot for image glyph view - "Images" button is on
    else:

        # create figure with mouse over, lasso, tap, pan, and zoom tools
        tools = ['box_zoom', 'pan', 'zoom_out', 'zoom_in', 'reset', 'tap', lasso]
        p = figure(logo=None, tools=tools, title=PLOT_TITLE)

        # add square - needed for tap tool callbacks
        p.square(x=x_axis, y=y_axis, size=25, source=source)

        # add image glyphs based using original image size
        p.image_url(x=x_axis, y=y_axis, url=THUMBS, h=None, w=None, source=source, anchor="center")

    # url = "http://127.0.0.1:5000/explore/00000013_005.png"
    url = "http://127.0.0.1:5000/explore/" + "default/" + "@{Image Index}"

    # create tap tool and connect to plot
    taptool = p.select(type=TapTool)

    # on click open new page with full-sized image
    taptool.callback = OpenURL(url=url)

    # return the complete plot with all tools
    p.plot_width = 1500
    p.plot_height = 800

    return p


# callback function to update visualization using new values from selection widgets
def update_plot(attr, old, new):

    # update x-axis category
    global x_axis
    x_axis = x.value

    # update y-axis category
    global y_axis
    y_axis = y.value

    # update coloration category
    global color_cat
    color_cat = color.value

    # add new child to layout with new plot
    global layout
    layout.children[0] = visualise()

# callback function for image-glyph function
def toggle_callback(active):

    # switch global toggle value to active (True if button clicked)
    global toggle_val
    toggle_val = active

    # add new child to layout with updated plot
    global layout
    layout.children[0] = visualise()

# function to create table based on table_source CDSView - returns the a DataTable object
def create_table():

    # create list of TableColumn objects TODO: reverse order maybe and don't include file path columns
    table_cols = []
    for col in table_source.source.column_names:
        # create TableColumn object with column
        if col != 'imgs' and col != 'thumbs' and col != 'index':
        # if col in {'Image Index', 'Patient Gender', 'Finding Labels', 'PCA_X', 'PCA_Y'}:
            new_col = [TableColumn(field=col, title=col)]

            # append column to list
            table_cols = new_col + table_cols

    # create DataTable object using TableColumn objects in list
    data_table = DataTable(source=source, columns=table_cols, view=table_source, width=1500)
    return data_table

# callback function for changes in plot selection
def selection_callback(attr, old, new):

    # indicies of selected points
    inds = np.array(new['1d']['indices'])

    # if no points selected, table_source CDSView is unfiltered
    global table_source
    if len(inds) == 0:
        table_source = CDSView(source=source)

    # otherwise filter the table_source CDSView to show only points selected
    else:
        table_source = CDSView(source=source, filters=[IndexFilter(inds)])

    # update third panel of layout to show new table
    layout.children[2] = create_table()


#MAIN PROGRAM - Must be oustside of function for curdoc() uplates to work

# open pickle file
df = pd.read_pickle(FILE_PATH)
columns = sorted(df.columns) # column names sorted

discrete = [col for col in columns if df[col].dtype == object] # columns with object/categorical variables
countable = [col for col in discrete if len(df[col].unique()) <= COUNTABLE_LIMIT] # columns to be used for color options
continuous = [col for col in columns if col not in discrete] # columns with continueous variables (for axis options)

# get rid of null error
for key in df:
        df[key] = ['NaN' if pd.isnull(value) else value for value in df[key]]

# set Bokeh ColumnDataSource to dataframe values
source = ColumnDataSource(df)

# init table_source to an unfiltered CDSView of source
table_source = CDSView(source=source)

# intitialise dropdown selection widget variables
x_axis = X_INIT
y_axis = Y_INIT
color_cat = COLOR_INIT
toggle_val = TOGGLE_INIT

# init Bokeh server document
doc = curdoc()

# create initial data table
data_table = create_table()
data_table.width = 1500

# create x-axis dropdown widget with continuous var columns
x = Select(title='X-Axis', value=X_INIT, options=continuous)
# link widget callback to update_plot()
x.on_change('value', update_plot)

# create y-axis dropdown widget with continuous var columns
y = Select(title='Y-Axis', value=Y_INIT, options=continuous)
# link widget callback to update_plot()
y.on_change('value', update_plot)

# create dot color dropdown widget with "countable" var columns
color = Select(title='Color', value=COLOR_INIT, options=countable)
# link widget callback to update_plot()
color.on_change('value', update_plot)

# create image glyph toggle button
toggle = Toggle(label="Show Images", button_type="success")
# link button callback to toggle_callback()
toggle.on_click(toggle_callback)

# create lasso
lasso = LassoSelectTool()

# download button
button = Button(label="Download", button_type="success")

# button.callback = download_callback()
button.callback = CustomJS(args=dict(source=source),
                           code=open(join(dirname(__file__), "download.js")).read())

# add button and dropdown selections to a widgetbox
widgets = [x, y, color, toggle, button]
controls = widgetbox(widgets, sizing_mode='scale_both')

# overall layout with plot, widgetbox, and the table
plot = visualise()

layout = column(plot, controls, data_table)

# update Bokeh server document with full layout
curdoc().add_root(layout)
