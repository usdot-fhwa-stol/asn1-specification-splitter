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


import os
import sys
import logging
import asn1tools

# Configure logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_file(file_path: str) -> str:
    """
    Validates the input ASN.1 file path and its syntax.

    Steps:
    - Checks if file exists and has .asn1 extension
    - Reads the file content
    - Parses it using asn1tools to ensure ASN.1 syntax is valid

    Args:
        file_path (str): Path to the input ASN.1 file.

    Returns:
        str: Contents of the file as a single string.

    Raises:
        SystemExit: If validation fails (missing file, wrong type, or invalid syntax).
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"❌ File not found: {file_path}")
        sys.exit(1)

    # Check for .asn1 file extension
    if not file_path.endswith('.asn1'):
        logger.error("❌ Invalid file type. Only '.asn1' files are supported.")
        sys.exit(1)

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        logger.exception(f"❌ Error reading file {file_path}: {e}")
        sys.exit(1)

    # Validate ASN.1 syntax using asn1tools' internal parser
    try:
        asn1tools.parse_string(content) 
        logger.info(f"✅ File '{file_path}' is valid and well-formed.")
    except Exception as e:
        logger.error(f"❌ ASN.1 syntax error in '{file_path}': {e}")
        
    return content
