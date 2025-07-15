import os
import sys
import shutil
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from dependency_resolver.resolver import clean_string, build_dependency_matrix, resolve_dependencies

@pytest.fixture(scope="module")
def setup_temp_schema_files():
    temp_schema_dir = "temp_test_schemas"
    os.makedirs(temp_schema_dir, exist_ok=True)

    schemas = {
        "Position3D.asn1": "Position3D ::= SEQUENCE { x INTEGER, y INTEGER }",
        "MessageFrame.asn1": "MessageFrame ::= SEQUENCE { pos Position3D, msgId DSRCmsgID }",  
        "VehicleStatus.asn1": "VehicleStatus ::= SEQUENCE { speed INTEGER, loc Position3D }",
        "DSRCmsgID.asn1": "DSRCmsgID ::= INTEGER (0..32767)"
    }

    for filename, content in schemas.items():
        with open(os.path.join(temp_schema_dir, filename), "w") as f:
            f.write(content)

    yield temp_schema_dir

    shutil.rmtree(temp_schema_dir)

def test_clean_string():
    assert clean_string("Position3D") == "Position3D"
    assert clean_string("Position3D-Location") == "Position3D-Location"
    assert clean_string("Position3D::=") == "Position3D"
    assert clean_string("SomeType(123)") == "SomeType123"
    assert clean_string("Speed@Loc") == "SpeedLoc"

def test_build_dependency_matrix(setup_temp_schema_files):
    schema_dir = setup_temp_schema_files
    schema_files = ["Position3D.asn1", "MessageFrame.asn1", "VehicleStatus.asn1"]
    schema_names = [f.split(".")[0] for f in schema_files]
    asn1_definitions = {"DSRCmsgID": True}

    dependency_matrix = build_dependency_matrix(schema_files, asn1_definitions, schema_names, schema_dir=schema_dir)

    expected = {
        "Position3D": [],
        "MessageFrame": ["Position3D", "DSRCmsgID"],
        "VehicleStatus": ["Position3D"]
    }

    assert set(dependency_matrix["MessageFrame"]) == {"Position3D", "DSRCmsgID"}
    assert dependency_matrix["Position3D"] == []
    assert dependency_matrix["VehicleStatus"] == ["Position3D"]

def test_resolve_dependencies():
    direct_deps = {
        "MessageFrame": ["Position3D"],
        "VehicleStatus": ["Position3D"],
        "Position3D": []
    }

    combined = resolve_dependencies(direct_deps)

    expected = {
        "MessageFrame": ["Position3D"],
        "VehicleStatus": ["Position3D"],
        "Position3D": []
    }

    assert combined == expected
