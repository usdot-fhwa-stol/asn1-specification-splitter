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
import sys
import asn1tools

#  Read ASN.1 file path from command line
if len(sys.argv) < 2:
    print("Usage: python validate_asn1_messages.py <path_to_asn1_file>")
    sys.exit(1)

ASN1_FILE = sys.argv[1]
OUTPUT_DIR = os.path.join("..", "data", "output", "messages")


def extract_message_types_from_asn1(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    inside_block = False
    message_lines = []

    for line in lines:
        if not inside_block and "MessageTypes" in line and "::=" in line:
            inside_block = True
            continue

        if inside_block:
            if "..." in line:
                break
            message_lines.append(line.strip())

    matches = []
    for line in message_lines:
        m = re.match(r'\{\s*(\w+)\s+IDENTIFIED\s+BY\s+\w+\s*\}', line)
        if m:
            matches.append(m.group(1))

    print(f"\n Extracted {len(matches)} message types:\n{matches}\n")
    return sorted(matches)


def validate_extension_in_output_folder():
    print("Checking for invalid extensions in output folder...")
    non_asn1_files = [
        f for f in os.listdir(OUTPUT_DIR)
        if os.path.isfile(os.path.join(OUTPUT_DIR, f)) and not f.endswith('.asn1')
    ]
    if non_asn1_files:
        print(f"\n Found {len(non_asn1_files)} file(s) with invalid extensions:")
        for file in non_asn1_files:
            print(f" - {file}")
    else:
        print(" All files in output folder have '.asn1' extension")
    print("-" * 60)


def main():
    validate_extension_in_output_folder()

    message_types = extract_message_types_from_asn1(ASN1_FILE)

    for message_type in message_types:
        expected_file = os.path.join(OUTPUT_DIR, f"{message_type}.asn1")

        print(f"\nChecking: {message_type}")

        # Check 1: File existence
        if not os.path.isfile(expected_file):
            print(f"Missing: {expected_file}")
            continue
        else:
            print("File exists")

        # Check 2: Extension
        if not expected_file.endswith('.asn1'):
            print("Invalid file extension")
            continue
        else:
            print("Extension is valid")

        # Check 3: Compile with asn1tools
        try:
            asn1tools.compile_files([expected_file], 'uper')
            print("Validation successful : no missing dependecies or syntax errors")
        except Exception as e:
            print(f"Validation failed: {e}")

        print("-" * 60)


if __name__ == "__main__":
    main()
