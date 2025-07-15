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
    definitions_dir = os.path.join("data", "files", "definitions")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(messages_dir, exist_ok=True)
    os.makedirs(definitions_dir, exist_ok=True)

    # Create some dummy schema files
    schemas = {
        "Position3D.asn1": "Position3D ::= SEQUENCE { x INTEGER, y INTEGER }",
        "MessageFrame.asn1": "MessageFrame ::= SEQUENCE { pos Position3D, msgId DSRCmsgID }",
    }
    for filename, content in schemas.items():
        with open(os.path.join(input_dir, filename), "w") as f:
            f.write(content)

    # Create a dummy definition file in definitions_dir
    with open(os.path.join(definitions_dir, "DSRCmsgID.asn1"), "w") as f:
        f.write("DSRCmsgID ::= INTEGER (0..32767)")

    yield input_dir, output_dir, messages_dir, definitions_dir

    # Cleanup after tests
    shutil.rmtree(input_dir)
    shutil.rmtree(output_dir)
    shutil.rmtree(definitions_dir, ignore_errors=True)

def test_merge_dependencies(setup_temp_schema_dirs):
    input_dir, output_dir, _, _ = setup_temp_schema_dirs

    # Pass both files so the dependency logic works!
    schema_files = ["MessageFrame.asn1", "Position3D.asn1"]
    combined_deps = {
        "MessageFrame": ["Position3D"]
    }

    merge_dependencies(schema_files, {}, combined_deps, input_dir=input_dir, output_dir=output_dir)

    output_file = os.path.join(output_dir, "MessageFrame.asn1")
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        merged_content = f.read()

    assert "MessageFrame ::=" in merged_content
    assert "Position3D ::=" in merged_content

def test_merge_dependencies_with_asn1_definitions(setup_temp_schema_dirs):
    input_dir, output_dir, _, definitions_dir = setup_temp_schema_dirs

    schema_files = ["MessageFrame.asn1", "Position3D.asn1"]
    asn1_definitions = {"DSRCmsgID": True}
    combined_deps = {
        "MessageFrame": ["Position3D", "DSRCmsgID"]
    }

    merge_dependencies(schema_files, asn1_definitions, combined_deps, input_dir=input_dir, output_dir=output_dir)

    output_file = os.path.join(output_dir, "MessageFrame.asn1")
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        merged_content = f.read()

    assert "MessageFrame ::=" in merged_content
    assert "Position3D ::=" in merged_content
    assert "DSRCmsgID ::=" in merged_content

def test_wrap_definitions(setup_temp_schema_dirs):
    input_dir, output_dir, _, _ = setup_temp_schema_dirs

    schema_files = ["MessageFrame.asn1", "Position3D.asn1"]
    combined_deps = {
        "MessageFrame": ["Position3D"]
    }
    merge_dependencies(schema_files, {}, combined_deps, input_dir=input_dir, output_dir=output_dir)

    wrap_definitions(["MessageFrame.asn1"], target_dir=output_dir)

    output_file = os.path.join(output_dir, "MessageFrame.asn1")
    with open(output_file, "r") as f:
        content = f.read()

    assert "MessageFrame DEFINITIONS AUTOMATIC TAGS::= BEGIN" in content or \
           "MessageFrame DEFINITIONS ::= BEGIN" in content
    assert content.strip().endswith("END")

def test_verify_syntax(setup_temp_schema_dirs):
    input_dir, output_dir, _, _ = setup_temp_schema_dirs

    schema_files = ["MessageFrame.asn1", "Position3D.asn1"]
    combined_deps = {
        "MessageFrame": ["Position3D"]
    }
    merge_dependencies(schema_files, {}, combined_deps, input_dir=input_dir, output_dir=output_dir)
    wrap_definitions(["MessageFrame.asn1"], target_dir=output_dir)

    error_log_path = os.path.join(output_dir, "errors.json")
    verify_syntax(["MessageFrame.asn1"], target_dir=output_dir, error_log_path=error_log_path)

    assert not os.path.exists(error_log_path)

def test_copy_message_deps(setup_temp_schema_dirs):
    input_dir, output_dir, messages_dir, _ = setup_temp_schema_dirs

    schema_files = ["MessageFrame.asn1", "Position3D.asn1"]
    combined_deps = {
        "MessageFrame": ["Position3D"]
    }
    merge_dependencies(schema_files, {}, combined_deps, input_dir=input_dir, output_dir=output_dir)
    wrap_definitions(["MessageFrame.asn1"], target_dir=output_dir)

    deps = {
        "MessageTypes": ["MessageFrame"]
    }

    copy_message_deps(deps, src_dir=output_dir, dest_dir=messages_dir)

    copied_file = os.path.join(messages_dir, "MessageFrame.asn1")
    assert os.path.exists(copied_file)


