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
import json
import logging
import shutil
import asn1tools

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_dependencies(schema_files, combined_deps, input_dir="data/files/schema", output_dir="data/files/schema_updated"):
    """
    Merges schema files with their transitive dependencies and writes the combined content to a new directory.

    Args:
        schema_files (list[str]): List of schema file names.
        combined_deps (dict): Mapping of schema file names to their transitive dependencies.
        input_dir (str): Directory containing base schema files.
        output_dir (str): Directory to write the merged schema files.
    """
    os.makedirs(output_dir, exist_ok=True)

    for schema_file in schema_files:
        name = schema_file.split(".")[0]
        base_path = os.path.join(input_dir, schema_file)

        try:
            with open(base_path, 'r', encoding='utf-8') as f:
                data = f.read()

            

            for dep in combined_deps.get(name, []):
                dep_path = os.path.join(input_dir, f"{dep}.asn1")
                with open(dep_path, 'r', encoding='utf-8') as dep_file:
                    data += dep_file.read()

            out_path = os.path.join(output_dir, schema_file)
            with open(out_path, 'w', encoding='utf-8') as out_file:
                out_file.write(data)

        except Exception as e:
            logger.error(f"Failed to merge schema: {schema_file}. Reason: {e}")

def wrap_definitions(schema_files, target_dir="data/files/schema_updated"):
    """
    Wraps each ASN.1 file in `DEFINITIONS ::= BEGIN ... END` block.

    Args:
        schema_files (list[str]): List of schema filenames.
        target_dir (str): Directory containing updated schema files.
    """
    for schema_file in schema_files:
        file_path = os.path.join(target_dir, schema_file)
        name = schema_file.split(".")[0]

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.read().splitlines()

           

            # Prepend and append definition markers
            wrapped_lines = [f"{name} DEFINITIONS ::= BEGIN"] + lines + ["END"]

            with open(file_path, 'w', encoding='utf-8') as file:
                for line in wrapped_lines:
                    file.write(line + '\n')

        except Exception as e:
            logger.error(f"Failed to wrap ASN.1 definitions in {schema_file}: {e}")

def verify_syntax(schema_files, target_dir="data/files/schema_updated", error_log_path="error_files.json"):
    """
    Verifies ASN.1 syntax and structural correctness using asn1tools' internal parser.

    This does NOT compile to encoding/decoding rules but ensures the file is well-formed.

    Args:
        schema_files (list[str]): List of schema filenames to check.
        target_dir (str): Directory where schema files are located.
        error_log_path (str): Path to output JSON file containing syntax errors.
    """
    error_count = 0

    for schema_file in schema_files:
        file_path = os.path.join(target_dir, schema_file)
      

        try:
            # Use parse_files to parse the syntax and validate syntax
            asn1tools.parse_files(file_path)
            # print(f"Syntax check passed for {schema_file}")

        except Exception as e:
            print(f"Something went wrong with {schema_file}: {e}")
            error_count += 1

    return error_count



def copy_message_deps(deps, src_dir="data/files/schema_updated", dest_dir="data/output/messages"):
    """
    Copies ASN.1 schema files listed under 'MessageTypes' dependency group to a separate folder.

    Args:
        deps (dict): Dependency map that includes a 'MessageTypes' key.
        src_dir (str): Source directory containing compiled schema files.
        dest_dir (str): Destination directory for message files.
    """
    os.makedirs(dest_dir, exist_ok=True)

    for message in deps.get('MessageTypes', []):
        src_path = os.path.join(src_dir, f"{message}.asn1")
        dest_path = os.path.join(dest_dir, f"{message}.asn1")

        try:
            shutil.copy(src_path, dest_path)
            
        except Exception as e:
            logger.error(f"Failed to copy {message}.asn1 to messages directory: {e}")
