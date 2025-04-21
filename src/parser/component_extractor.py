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
import re
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    # Replace or remove invalid characters for filenames
    return re.sub(r'[<>:"/\\|?*= ]+', "", name)


def extract_components(namespace_files, input_dir="data/files/namespace", output_dir="data/files/schema"):
    """
    Extracts individual components from each ASN.1 namespace file and writes them as separate schema files.

    A component is defined as a block starting with a line containing '::=' and ending before the next such line.

    Args:
        namespace_files (list[str]): List of filenames present in the namespace directory.
        input_dir (str): Path to the namespace directory. Default is 'src/files/namespace'.
        output_dir (str): Path to the output schema directory. Default is 'src/files/schema'.
    """
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    for filename in namespace_files:
        input_path = os.path.join(input_dir, filename)

        try:
            with open(input_path, 'r', encoding='utf-8') as file:
                data = file.read()
        except Exception as e:
            logger.error(f"Failed to read file {input_path}: {e}")
            continue

        # Remove the first and last two lines (which contain namespace BEGIN/END)
        lines = data.splitlines()[1:-2]
        lines_count = len(lines)

        count = 0
        components = {}
        component_name = ""
        start = 0

        while count < lines_count:
            line = lines[count]

            # Strip comments from the line
            if "--" in line:
                line = line.split("--")[0]

            # Detect start of a new component block
            if "::=" in line:
                if component_name:
                    # Save the previously identified component
                    components[component_name] = {"start": start + 1, "end": count}
                component_name = line.split()[0]
                start = count

            count += 1

        # Add the final component if any
        if component_name:
            components[component_name] = {"start": start, "end": count}

        # Write each top-level component to its own file
        for comp_name in components:
            if comp_name[0].islower():
                continue  # Skip components starting with lowercase (often private/internal)

            safe_name = sanitize_filename(comp_name)
            output_path = os.path.join(output_dir, f"{safe_name}.asn1")

            try:
                with open(output_path, 'w') as file:
                    for j in range(components[comp_name]["start"] - 1, components[comp_name]["end"]):
                        file.write(lines[j] + '\n')
                # logger.info(f"Component '{comp_name}' written to: {output_path}")
            except Exception as e:
                logger.error(f"Failed to write component {comp_name} to file: {e}")


def remove_namespace_references(schema_files, available_namespaces, schema_dir="data/files/schema"):
    """
    Removes namespace prefixes (e.g., Namespace.Component) from schema files.

    Args:
        schema_files (list[str]): List of schema filenames to process.
        available_namespaces (list[str]): List of namespace prefixes to strip.
        schema_dir (str): Directory where schema files are located.
    """
    for schema_file in schema_files:
        file_path = os.path.join(schema_dir, schema_file)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                # logger.info(f"Processing schema file: {schema_file}")

            # Replace namespace prefixes like 'NS.' with ''
            for ns in available_namespaces:
                data = data.replace(ns + ".", "")

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(data)
        except Exception as e:
            logger.error(f"Error processing {schema_file}: {e}")
