# PYTHON3ML="/Library/Frameworks/Python.framework/Versions/3.6/bin/python3"
# echo "Setting python path to "${PYTHON3ML}
echo "Creating virtual environment under ./env"
# ${PYTHON3ML} -m virtualenv ./medicalDataVisul # Create a virtual environment (python3)
virtualenv ./medicalDataVisul
echo "Install requirements"
source medicalDataVisul/bin/activate
which python3
pip install -r requirements.txt --no-cache-dir
deactivate
unset PYTHON3ML
echo "Finished und unset python path"
