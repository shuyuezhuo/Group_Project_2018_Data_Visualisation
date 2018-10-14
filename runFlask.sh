# PYTHON3ML="/Library/Frameworks/Python.framework/Versions/3.6/bin/python3"
# echo "Setting python path to "${PYTHON3ML}
echo "Opening virtual environment"
source ./medicalDataVisul/bin/activate
cd ./src/webapp
pip install --editable .
export FLASK_APP=webapp
flask run
