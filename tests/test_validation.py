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
import pytest
import sys
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from validation.file_validator import validate_file

# --- Fixture to create and clean up temp ASN.1 files ---
@pytest.fixture
def valid_asn1_file():
    content = """
MyModule DEFINITIONS ::= BEGIN
MyType ::= INTEGER
END
""".strip()
    fd, path = tempfile.mkstemp(suffix=".asn1")
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(content)
    yield path
    os.remove(path)

@pytest.fixture
def invalid_asn1_file():
    content = """
MyModule DEFINITIONS ::= BEGIN
MyType ::= INTEGER -- missing END
"""  # syntax error: no END

    fd, path = tempfile.mkstemp(suffix=".asn1")
    with os.fdopen(fd, 'w') as tmp:
        tmp.write(content)
    yield path
    os.remove(path)

@pytest.fixture
def non_asn1_file():
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, 'w') as tmp:
        tmp.write("This is not an ASN.1 file")
    yield path
    os.remove(path)

# --- TEST CASES ---

def test_valid_file_passes_validation(valid_asn1_file):
    result = validate_file(valid_asn1_file)
    assert "MyType ::= INTEGER" in result

def test_missing_file_exits():
    with pytest.raises(SystemExit):
        validate_file("non_existent_file.asn1")

def test_wrong_extension_triggers_exit(non_asn1_file):
    with pytest.raises(SystemExit):
        validate_file(non_asn1_file)

# def test_invalid_syntax_file_triggers_exit(invalid_asn1_file):
#     with pytest.raises(SystemExit):
#         validate_file(invalid_asn1_file)
 
