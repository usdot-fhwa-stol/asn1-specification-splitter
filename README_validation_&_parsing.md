# Validation & Parsing Modules
This document describes the  usage of the **Validation** and **Parsing** components of the ASN.1 splitter system. These modules handle the initial reading, syntax checking, and structured parsing of ASN.1 files into manageable namespaces and components.

### Set up Environment
- Setting up a virtual environment in the root directory and run the following commands:
    -  python -m venv venv   (or) python3 -m venv venv
    -  For MacOS
        - . ./venv/bin/activate 
    -  For Windows
        - venv/scripts/activate

- Once inside the root directory run:
    - pip install asn1tools
    - pip insyall pytest

- Your environment to run .py files will be ready after installation.


### Execution

- Setup environment and make sure venv is activated before proceeding to next steps.

- Once virutal environment is activated. 
    - Navigate to the directory in which main.py is present. 
    - Make sure to have the input file path.
    - To run the file use "python -m src.main.py <file_path>".
    - It's best practice to have the input file inside the project directory "data/input"
    - Once the program runs successfully you can find the namespace and schema files inside directory "data/files".
- Tests 
    - To run test navigate to the root directory.
    - Use command "pytest tests/test_validation.py" for validation test
    - Use command "pytest tests/test_Parser.py" for Parser test
