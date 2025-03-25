import sys
import os

from src.parser.component_extractor import extract_components, remove_namespace_references
from src.parser.namespace_extractor import extract_namespaces, write_namespace_files
from src.validation.file_validator import  validate_file

def print_banner():
    """
    Prints a stylized ASCII welcome banner.
    """
    banner = r"""
*************************************************
*                                               *
*       WELCOME TO ASN.1 SCHEMA SPLITTER        *
*                                               *
*************************************************
"""
    print(banner)

# --- Main script execution starts here ---
file_path = sys.argv[1]

print_banner()

# Step 0: Validate and load the ASN.1 file
print("\n🔍 Validating and loading ASN.1 file...")
data = validate_file(file_path)
lines = data.splitlines()

# Step 1: Extract namespaces and write to individual files
print("\n📂 Step 1: Extracting namespaces and saving to files...")
namespaces = extract_namespaces(lines)
write_namespace_files(namespaces, lines)
namespace_files = os.listdir("data/files/namespace")

# Step 2: Extract top-level components from namespace files
print("\n📦 Step 2: Extracting components from namespace files...")
extract_components(namespace_files)
schema_files = os.listdir("data/files/schema")
schema_names = [i.split(".")[0] for i in schema_files]

# Step 3: Remove namespace references within schemas
print("\n🧹 Step 3: Removing namespace references from schemas...")
remove_namespace_references(schema_files, list(namespaces))
