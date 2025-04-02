# Copyright (C) 2025 LEIDOS.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import sys
import os

from src.parser.component_extractor import extract_components, remove_namespace_references
from src.parser.namespace_extractor import extract_namespaces, write_namespace_files
from src.validation.file_validator import  validate_file

import os

def ensure_data_directories():
    """
    Ensures all required directories under 'data/' exist.
    If they do not exist, they will be created.
    """
    required_dirs = [
        "data/input",
        "data/output",
        "data/files/namespace",
        "data/files/schema"
    ]

    for path in required_dirs:
        os.makedirs(path, exist_ok=True)  # Creates directory if missing


def print_banner():
    """
    Prints a stylized ASCII welcome banner.
    """
    banner = r"""
*************************************************
*                                               *
*       WELCOME TO ASN.1 SCHEMA SPLITTER        *
*                                               *
*************************************************
"""
    print(banner)

# --- Main script execution starts here ---
file_path = sys.argv[1]

#Ensure required folders are present
ensure_data_directories()

print_banner()

# Step 0: Validate and load the ASN.1 file
print("\n Validating and loading ASN.1 file...")
data = validate_file(file_path)
lines = data.splitlines()

# Step 1: Extract namespaces and write to individual files
print("\n Step 1: Extracting namespaces and saving to files...")
namespaces = extract_namespaces(lines)
write_namespace_files(namespaces, lines)
namespace_files = os.listdir("data/files/namespace")

# Step 2: Extract top-level components from namespace files
print("\n Step 2: Extracting components from namespace files...")
extract_components(namespace_files)
schema_files = os.listdir("data/files/schema")
schema_names = [i.split(".")[0] for i in schema_files]

# Step 3: Remove namespace references within schemas
print("\n Step 3: Removing namespace references from schemas...")
remove_namespace_references(schema_files, list(namespaces))
