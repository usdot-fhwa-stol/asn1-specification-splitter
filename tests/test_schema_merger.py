import os
import shutil
import pytest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from consolidator.schema_merger import (
    merge_dependencies,
    wrap_definitions,
    verify_syntax,
    copy_message_deps
)

@pytest.fixture(scope="module")
def setup_temp_schema_dirs():
    """
    Set up temporary input/output schema directories for testing.
    """
    input_dir = "temp_schema_input"
    output_dir = "temp_schema_output"
    messages_dir = os.path.join(output_dir, "messages")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(messages_dir, exist_ok=True)

    # Create some dummy schema files
    schemas = {
        "Position3D.asn1": "Position3D ::= SEQUENCE { x INTEGER, y INTEGER }",
        "MessageFrame.asn1": "MessageFrame ::= SEQUENCE { pos Position3D }",
    }

    for filename, content in schemas.items():
        with open(os.path.join(input_dir, filename), "w") as f:
            f.write(content)

    yield input_dir, output_dir, messages_dir

    # Cleanup after tests
    shutil.rmtree(input_dir)
    shutil.rmtree(output_dir)

def test_merge_dependencies(setup_temp_schema_dirs):
    input_dir, output_dir, _ = setup_temp_schema_dirs

    schema_files = ["MessageFrame.asn1"]
    combined_deps = {
        "MessageFrame": ["Position3D"]
    }

    merge_dependencies(schema_files, combined_deps, input_dir=input_dir, output_dir=output_dir)

    output_file = os.path.join(output_dir, "MessageFrame.asn1")
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        merged_content = f.read()

    # Should contain content from both MessageFrame and Position3D
    assert "MessageFrame ::=" in merged_content
    assert "Position3D ::=" in merged_content

def test_wrap_definitions(setup_temp_schema_dirs):
    _, output_dir, _ = setup_temp_schema_dirs

    schema_files = ["MessageFrame.asn1"]
    wrap_definitions(schema_files, target_dir=output_dir)

    output_file = os.path.join(output_dir, "MessageFrame.asn1")
    with open(output_file, "r") as f:
        content = f.read()

    assert "MessageFrame DEFINITIONS ::= BEGIN" in content
    assert content.strip().endswith("END")

def test_verify_syntax(setup_temp_schema_dirs):
    _, output_dir, _ = setup_temp_schema_dirs

    schema_files = ["MessageFrame.asn1"]
    error_log_path = os.path.join(output_dir, "errors.json")

    verify_syntax(schema_files, target_dir=output_dir, error_log_path=error_log_path)

    # Should not create an error log if syntax is good
    assert not os.path.exists(error_log_path)

def test_copy_message_deps(setup_temp_schema_dirs):
    _, output_dir, messages_dir = setup_temp_schema_dirs

    deps = {
        "MessageTypes": ["MessageFrame"]
    }

    copy_message_deps(deps, src_dir=output_dir, dest_dir=messages_dir)

    copied_file = os.path.join(messages_dir, "MessageFrame.asn1")
    assert os.path.exists(copied_file)
