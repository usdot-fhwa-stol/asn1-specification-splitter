# Validation & Parsing Modules

This document describes the usage of the **Validation** and **Parsing** components of the ASN.1 splitter system. These modules handle the initial reading, syntax checking, and structured parsing of ASN.1 files into manageable namespaces and components.

---

## Setup Environment

> The following steps will create and activate a virtual environment, then install required dependencies. Ensure you are in the project root directory.


<summary>Setup Instructions (Ubuntu, macOS, Windows)</summary>

```bash
# Step 1: Create a virtual environment
python3 -m venv venv  # or use 'python -m venv venv'

# Step 2: Activate the virtual environment

# For Ubuntu/Linux
source venv/bin/activate  # This step activates the environment

# For macOS
. ./venv/bin/activate     # This step activates the environment

# For Windows
venv\Scripts\activate     # This step activates the environment

# Step 3: Install required packages
pip install asn1tools     # Install the ASN.1 tools library
pip install pytest        # Install pytest for running test cases
```



---

## Execution

> Make sure the virtual environment is activated before running the scripts.

```bash
# Step 1: Activate the virtual environment (see above)

# Step 2: Navigate to the directory where main.py is located

# Step 3: Run the main parser with input ASN.1 file
python -m src.main <file_path>  # Replace <file_path> with the actual file path

# Note: It's best to place the input file inside 'data/input'

# Step 4: After successful execution, output files will be saved in:
#         - data/files/ (contains generated namespace and schema files)
```

---

## Run Tests

```bash
# Step 1: Navigate to the project root directory
cd <project-root>  # Replace <project-root> with the actual root folder

# Step 2: Run validation test
pytest tests/test_validation.py

# Step 3: Run parser test
pytest tests/test_Parser.py
```
