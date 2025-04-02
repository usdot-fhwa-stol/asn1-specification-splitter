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
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_namespaces(lines):
    """
    Extracts ASN.1 namespaces from the given list of lines.

    A namespace is expected to start with a line containing "::= BEGIN" and end with a line containing "END".

    Args:
        lines (list[str]): Lines from the ASN.1 source file.

    Returns:
        dict: A dictionary mapping each namespace name to its start and end line indices.
              Example: {'NamespaceName': {'start': 10, 'end': 25}}
    """
    count = 0
    lines_count = len(lines)
    namespaces = {}
    namespace = None  # Track current namespace

    while count < lines_count:
        line = lines[count]
        
        # Detect namespace start
        if "::= BEGIN" in line:
            namespace = line.split()[0].strip()
            start = count

        # Detect namespace end and store the range
        if "END" in line and namespace:
            end = count + 1
            namespaces[namespace] = {"start": start, "end": end}
            # logger.debug(f"Namespace extracted: {namespace} (lines {start}-{end})")
            namespace = None  # Reset for next namespace

        count += 1

    if not namespaces:
        logger.warning("No namespaces found in the file.")

    return namespaces

def write_namespace_files(namespaces, lines, output_dir="data/files/namespace"):
    """
    Writes each ASN.1 namespace to a separate file.

    Args:
        namespaces (dict): Dictionary containing namespace names and their line ranges.
        lines (list[str]): List of lines from the original ASN.1 file.
        output_dir (str): Directory where namespace files will be stored. Defaults to 'src/files/namespace'.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for namespace, positions in namespaces.items():
        file_path = os.path.join(output_dir, f"{namespace}.asn1")
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for idx in range(positions["start"], positions["end"]):
                    file.write(lines[idx] + '\n')
            # logger.info(f"Written namespace '{namespace}' to: {file_path}")
        except Exception as e:
            logger.exception(f"Failed to write namespace '{namespace}' to file: {e}")
