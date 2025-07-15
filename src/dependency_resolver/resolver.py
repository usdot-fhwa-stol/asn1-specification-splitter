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
import re
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_string(s):
    """
    Removes all characters from a string except alphanumerics and hyphens.

    Args:
        s (str): Input string.

    Returns:
        str: Cleaned string with only letters, numbers, and hyphens.
    """
    return re.sub(r'[^a-zA-Z0-9-]', '', s)

def build_dependency_matrix(schema_files, asn1_definitions,schema_names, schema_dir="data/files/schema"):
    """
    Parses ASN.1 schema files to build a direct dependency matrix.

    For each file, it identifies referenced component names that are also schema files.

    Args:
        schema_files (list[str]): List of .asn1 filenames.
        schema_names (list[str]): List of valid component names (without .asn1).
        schema_dir (str): Directory where schema files are stored.

    Returns:
        dict: A mapping from each schema name to a list of its direct dependencies.
    """
    dependency_matrix = {}
    for schema_file in schema_files:
        dependencies = set()
        name = schema_file.split(".")[0]
        file_path = os.path.join(schema_dir, f"{name}.asn1")

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
        except Exception as e:
            logger.error(f"Error reading schema file {file_path}: {e}")
            continue

        lines = data.splitlines()

        for line in lines:
            if "::=" in line:
                line=line.split("::=")[1]

            # Strip inline comments
            if "--" in line:
                line = line.split("--")[0]

            words = line.split()

            for word in words:
                
                if "." in word and ".." not in word and "..." not in word:
                    new_words=word.split(".")
                    for new_word in new_words:
                        if new_word in schema_names and new_word!=name:
                            dependencies.add(new_word)

                word = clean_string(word)

                if word in asn1_definitions and word != name:
                    dependencies.add(word)

                # If a word matches another schema component and is not self-reference
                if word in schema_names and word != name:
                    dependencies.add(word)

        dependency_matrix[name] = list(dependencies)
        # logger.debug(f"Dependencies for {name}: {dependency_matrix[name]}")

    return dependency_matrix

def resolve_dependencies(deps):
    """
    Builds a transitive dependency map using depth-first traversal.

    For each schema/component, it collects all indirect dependencies recursively.

    Args:
        deps (dict): Direct dependency map (output of build_dependency_matrix).

    Returns:
        dict: Transitive (flattened) dependency map for each schema.
    """

    def get_deps(key, visited):
        """
        Recursively adds all transitive dependencies for a given component.

        Args:
            key (str): Component name.
            visited (set): Set of already visited components to avoid cycles.
        """
        if key in deps:
            for dep in deps[key]:
                if dep not in visited:
                    visited.add(dep)
                    get_deps(dep, visited)

    combined_deps = {}

    for key in deps:
        visited = set()

        if not deps[key]:  # No dependencies
            combined_deps[key] = []
        else:
            for dep in deps[key]:
                visited.add(dep)
                get_deps(dep, visited)
            combined_deps[key] = list(visited)

        # logger.debug(f"Transitive dependencies for {key}: {combined_deps[key]}")

    return combined_deps
