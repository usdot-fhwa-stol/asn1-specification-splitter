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

import sys
import re
import os
import json
import asn1tools
import shutil
from collections import deque

#accept multiple files
#check and validate for well formness of asn1 file by compiling input using asn1 tools

# take a file name as arg
file_path=sys.argv[1]

if file_path.endswith('.asn1'):
    with open(file_path, 'r') as file:
        data = file.read()
        # print(data)
else:
    print("Invalid file type")
    sys.exit(1)





# parse the file line by line to find ::= pattern
# if found, extract the schema name and type

lines=data.splitlines()
# print(lines)

count=0
lines_count=len(lines)
namesspaces=[]

dirs=["../files/schema","../files/schema_updated"]

for dir in dirs:
    if not os.path.exists(dir):
        os.makedirs(dir)

    files=os.listdir(dir)
    for file in files:
        os.remove(f"{dir}/{file}")


"""
Namespace parser
"""
isNamespace=False
start=0
end=0
namespaces={}
while count<lines_count:
    line=lines[count]
    if "::= BEGIN" in line:
        namespace=line.split()[0].strip()
        # print("Namespace:",namespace) 
        isNamespace=True
        start=count
    if "END" in line:
        isNamespace=False
        end=count
        end+=1
        namespaces[namespace]={
            "start":start,
            "end":end
        }
    
    count+=1

"""
    Write each namespace data to a file
"""
# print(namesspaces)
for i in namespaces:
    with open(f"../files/namespace/{i}.asn1",'w') as file:
        for j in range(namespaces[i]["start"],namespaces[i]["end"]):
            file.write(lines[j]+'\n')


namespace_files=os.listdir("../files/namespace")


"""
Parse Each file and load into Memory
"""
# possible_types=["ENUMERATED","INTEGER","CHOICE","IA5String","CLASS","BIT","SEQUENCE","BOOLEAN","OCTET"]
# schema_types=set()

def find_between_parentheses(s):
    return re.findall(r'\((.*?)\)', s)

mapper={}
constant_mapper={}
constants_data={}

for file in namespace_files:
    with open(f"../files/namespace/{file}",'r') as file:
        data=file.read()
        # print(data)
        # print("\n")


    lines=data.splitlines()
    lines=lines[1:-2]
    lines_count=len(lines)
    count=0
    components={}
    component_name=""
    start=0
    is_component=False
    # print(lines)

    while count<lines_count:
        line=lines[count]
        if "--" in line:
            line=line.split("--")[0]

        if "::=" in line:
            if component_name!="":
                components[component_name]={
                    "start":start+1,
                    "end":count
                }
            component_name=line.split()[0]
            start=count
        count+=1

    
    if component_name!="":
        components[component_name]={
            "start":start,
            "end":count
        }

    for i in components:
        if i[0].islower():
            continue
        with open(f"../files/schema/{i}.asn1",'w') as file:
            for j in range(components[i]["start"]-1,components[i]["end"]):
                file.write(lines[j]+'\n')

# with open("components.json",'w') as file:
#     json.dump(components,file,indent=4)

schema_files=os.listdir("../files/schema")
schema_names=[i.split(".")[0] for i in schema_files]

available_namespaces=[i for i in namespaces]
constant_names=[i for i in constant_mapper]

def clean_string(s):
    return re.sub(r'[^a-zA-Z0-9-]', '', s)  # Allow '-' in the string



"""
    Modify the words by removing namespace
"""
print(available_namespaces)

for schema_file in schema_files:
    with open(f"../files/schema/{schema_file}",'r') as file:
        data=file.read()
        print("Schema File:",schema_file)
        name=schema_file.split(".")[0]
        for i in available_namespaces:
            data=data.replace(i+".","")

    with open(f"../files/schema/{schema_file}",'w') as file:
        file.write(data)


dependency_matrix={}

for schema_file in schema_files:

    dependencies=set()
    updated_data=[]
    name=schema_file.split(".")[0]
    visited=set()
    with open(f"../files/schema/{name}.asn1",'r') as file:
        data=file.read()
        print("Schema File:",schema_file)
        
        lines=data.splitlines()
        for line in lines:
            updated_data.append(line)
        
        for line in lines:
            if "--" in line:
                line=line.split("--")[0]

            words=line.split()
            # print(words)
            for word in words:
                
                word=clean_string(word)

                if word in schema_names and word!=name:
                    dependencies.add(word)
                

    dependency_matrix[name]=list(dependencies)


deps={k: v for k, v in sorted(dependency_matrix.items(), key=lambda item: item[0])}
with open("deps.json",'w') as file:
    json.dump(deps,file,indent=4)


def get_deps(key,visited):
    if key in deps:
        for i in deps[key]:
            if i not in visited:
                visited.add(i)
                get_deps(i,visited)
    

combined_deps={}

for dep in deps:
    queue = deque()
    visited=set()
    if len(deps[dep])==0:
        combined_deps[dep]=deps[dep]

    else:
        for i in deps[dep]:
            visited.add(i)
            queue.append(i)
            get_deps(i,visited)
        combined_deps[dep]=list(visited)

        
         

with open("combined_deps.json",'w') as file:
    json.dump(combined_deps,file,indent=4)

for schema_file in schema_files:
    with open(f"../files/schema/{schema_file}",'r') as file:
        data=file.read()
        print("Schema File:",schema_file)
        name=schema_file.split(".")[0]
       
        ds=combined_deps[name]

        for d in ds:
            with open(f"../files/schema/{d}.asn1",'r') as file:
                data+=file.read()

    with open(f"../files/schema_updated/{schema_file}",'w') as file:
        file.write(data)
    


schema_files=os.listdir("../files/schema")
schema_names=[i.split(".")[0] for i in schema_files]

for schema_file in schema_files:
    with open(f"../files/schema_updated/{schema_file}",'r') as file:
        data=file.read()
        print("Schema File:",schema_file)
        name=schema_file.split(".")[0]
    
        lines=data.splitlines()

        lines=[f"{name} DEFINITIONS ::= BEGIN\n"]+lines+["END"]

    with open(f"../files/schema_updated/{schema_file}",'w') as file:
        for line in lines:
            file.write(line+'\n')

error_count=0
error_files={}
for file in schema_files:
    print("compiling file:",file)
    try:
        asn1tools.compile_files(f"../files/schema_updated/{file}", 'uper')
    except Exception as e:
        print("Error in file:",file)
        error_files[file]=str(e)
        print(e)
        error_count+=1
        print("\n\n")

print("Total Errors:",error_count)
print("Total Files:",len(schema_files))


with open("error_files.json",'w') as file:
    json.dump(error_files,file,indent=4)

for i in deps['MessageTypes']:    
    # copy the file from schema_updated dir to messages dir
    shutil.copy(f"../files/schema_updated/{i}.asn1", f"../files/messages/{i}.asn1")





# with open("constant_mapper.json",'w') as file:
#     json.dump(constant_mapper,file,indent=4)
