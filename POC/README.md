# POC for asn1 - splitter

### Introduction

- This proof of concept (PoC) was developed to validate the feasibility of the initial logic for processing ASN.1 files. It takes a monolithic ASN.1 file, identifies and extracts     individual namespaces and components, and splits them into modular, manageable .asn1 files. This approach enables better organization and dependency management. As the project evolves, this PoC will be extended into a fully-featured, production-grade solution built to meet industry standards and scalability requirements.


### Set up Environment

- Setting up a virtual environment in the root directory and run the following commands:
    -  python -m venv venv   (or) python3 -m venv venv
    -  For MacOS
        - . ./venv/bin/activate 
    -  For Windows
        - venv/scripts/activate


- Once inside the root directory run:
    - pip install asn1tools

- Your environment to run .py files will be ready after installation.

### Execution

- Setup environment and make sure venv is activated before proceeding to next steps.

- Once virutal environment is activated. 
    - Navigate to the directory in which parser.py is present. 
    - Make sure to have the input file path.
    - To run the file use python parser.py <file_path>.
    - Once the parser runs successfully you can find the individual files in messages.













