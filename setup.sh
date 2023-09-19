#!/bin/bash

# How to setup the environment for this Framework?
# Step 1 => Navigate to the root directory of this Project in the terminal. Mostly this will be Brakeman-comparison
# Step 2 => source setup.sh
# Step 3 => Enter the above command in the terminal and hit Enter
#        => Now an virtual environment will be created and all dependencies for this project will be installed
# Note: Reach out for any issues

# create a virtual environment using python venv (STANDARD LIBRARY)
python3 -m venv virtual_environment

# activate the virtual environment
source virtual_environment/bin/activate

# install dependencies from requirements.txt
pip3 install -r requirements.txt
