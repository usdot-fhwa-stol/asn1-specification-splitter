import os
import sys
import tempfile
import shutil
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from parser.namespace_extractor import extract_namespaces, write_namespace_files
from parser.component_extractor import extract_components, remove_namespace_references



@pytest.fixture
def sample_asn1_lines():
    return [
        "DSRC DEFINITIONS ::= BEGIN",
        "Message1 ::= SEQUENCE { id INTEGER }",
        "Message2 ::= SEQUENCE { name IA5String }",
        "Dummy ::= NULL",
        "END",
        "XYZ DEFINITIONS ::= BEGIN",
        "Example ::= CHOICE { option BOOLEAN }",
        "-- padding after XYZ",
        "Dummy2 ::= NULL",
        "END"
    ]


@pytest.fixture
def temp_dirs():
    """Creates temporary working directories and cleans up after test."""
    base = tempfile.mkdtemp()
    ns_dir = os.path.join(base, "namespace")
    schema_dir = os.path.join(base, "schema")
    os.makedirs(ns_dir)
    os.makedirs(schema_dir)
    yield {
        "base": base,
        "namespace_dir": ns_dir,
        "schema_dir": schema_dir
    }
    shutil.rmtree(base)


def test_extract_namespaces(sample_asn1_lines):
    result = extract_namespaces(sample_asn1_lines)
    assert "DSRC" in result
    assert "XYZ" in result
    assert result["DSRC"]["start"] == 0
    assert result["DSRC"]["end"] == 5
    assert result["XYZ"]["start"] == 5
    assert result["XYZ"]["end"] == 10


def test_write_namespace_files_and_extract_components(sample_asn1_lines, temp_dirs):
    namespaces = extract_namespaces(sample_asn1_lines)

    # Write each namespace to its own file
    write_namespace_files(namespaces, sample_asn1_lines, output_dir=temp_dirs["namespace_dir"])
    ns_files = os.listdir(temp_dirs["namespace_dir"])
    assert set(ns_files) == {"DSRC.asn1", "XYZ.asn1"}

    # Extract components from those files
    extract_components(ns_files, input_dir=temp_dirs["namespace_dir"], output_dir=temp_dirs["schema_dir"])
    schema_files = os.listdir(temp_dirs["schema_dir"])
    assert "Message1.asn1" in schema_files
    assert "Message2.asn1" in schema_files
    assert "Example.asn1" in schema_files

    # Check content of one file
    with open(os.path.join(temp_dirs["schema_dir"], "Message1.asn1")) as f:
        content = f.read()
        assert "id INTEGER" in content


def test_remove_namespace_references(temp_dirs):
    # Create a schema file with namespaced component references
    schema_path = os.path.join(temp_dirs["schema_dir"], "TestFile.asn1")
    with open(schema_path, "w") as f:
        f.write("DSRC.Message1 ::= SEQUENCE { id INTEGER }\nXYZ.Example ::= CHOICE { test BOOLEAN }")

    # Remove namespace prefixes
    remove_namespace_references(["TestFile.asn1"], ["DSRC", "XYZ"], schema_dir=temp_dirs["schema_dir"])

    with open(schema_path) as f:
        cleaned = f.read()
        assert "DSRC." not in cleaned
        assert "XYZ." not in cleaned
        assert "Message1" in cleaned
        assert "Example" in cleaned
