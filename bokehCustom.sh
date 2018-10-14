source ./medicalDataVisul/bin/activate
cd ./src/webapp/webapp
bokeh serve --port 5005 --allow-websocket-origin=127.0.0.1:5000 bokehapp_custom
