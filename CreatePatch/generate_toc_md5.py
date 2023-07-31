# This script will generate the first 16 bits of a .SIG file used to validate wow interface (addons & frameXML).
# The .SIG file needs to exists already in the same directory as the toc file.
# This is not enough to make a working .SIG file accepted by the 335 client, there is also another SHA1 check validating the .SIG file itself.
# Usage: generate_md5.py <path_to_toc_file>

import hashlib
import os
import sys
import xml.etree.ElementTree as ET

class CustomError(Exception):
    pass
    
def update_md5_from_xml_recursive(md5_context, dirname, element, tags):
    for child in element:
        tag_without_namespace = child.tag.split('}')[-1]  # Extract local tag name without namespace
        if tag_without_namespace in tags:
            file_attribute = child.get('file')
            if file_attribute is not None:
                update_md5_hash(md5_context, dirname + '/' + file_attribute)
                
        update_md5_from_xml_recursive(md5_context, dirname, child, tags)

def update_md5_from_toc(md5_context, dirname, file):
    file.seek(0)
    for line in file:
        line = line.strip()  # Remove leading/trailing whitespace
        if line and not line.startswith(b'#'):
            new_path = dirname + '/' + line.decode()
            update_md5_hash(md5_context, new_path)
    return

def update_md5_from_xml(md5_context, dirname, xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        tags = ['Script', 'Include']
        update_md5_from_xml_recursive(md5_context, dirname, root, tags)

    except ET.ParseError as e:
        raise CustomError(f"Error parsing XML file: {str(e)}")
    except FileNotFoundError:
        raise CustomError(f"File '{xml_file}' not found.")
    except Exception as e:
        raise CustomError(f"An error occurred: {str(e)}")
    return

def update_md5_hash(md5_context, file_path):
    try:
        file_name = os.path.basename(file_path)
        print('Opening ' + file_name)
        dirname = os.path.dirname(file_path)
        with open(file_path, 'rb') as file:
            contents = file.read()
            md5_context.update(contents)
            
            file_extension = os.path.splitext(file_path)[1]
            if file_extension == '.toc':
                update_md5_from_toc(md5_context, dirname, file)
            elif file_extension == '.xml':
                update_md5_from_xml(md5_context, dirname, file_path)

            return
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        # some files seem to be just missing from blizz ui.. like Blizzard_InspectUI/PVPFrameTemplates.xml referenced in InspectPVPFrame.xml
    except PermissionError:
        raise CustomError(f"Permission denied to access file '{file_path}'.")
    except Exception as e:
        raise CustomError(f"An error occurred: {str(e)}")

def write_hash_to_file(file_path, md5_hash):
    try:
        with open(file_path, 'r+b') as file:
            file.seek(0)
            file.write(md5_hash)
        file_name = os.path.basename(file_path)
        print(f"MD5 hash successfully written to '{file_name}'.")
    except FileNotFoundError:
        raise CustomError(f"File '{file_path}' not found.")
    except PermissionError:
        raise CustomError(f"Permission denied to access file '{file_path}'.")
    except Exception as e:
        raise CustomError(f"An error occurred while writing to '{file_path}': {str(e)}")

def process_file(input_file_path):
    output_file_path = input_file_path.upper() + '.SIG'
    output_file_name = os.path.basename(output_file_path)
    print(f"Outputting to {output_file_name}")
    md5_context = hashlib.md5()

    update_md5_hash(md5_context, input_file_path)

    # Also if there is a Bindings.xml file in the same directory, update md5 with it
    # UNTESTED for now
    dirname = os.path.dirname(input_file_path)
    bindings_filename = dirname + '/' + "Bindings.xml"
    try:
        with open(bindings_filename, 'rb') as file:
            contents = file.read()
            md5_context.update(contents)
    except FileNotFoundError:
        pass
        #print("(No Bindings.xml file found)")

    md5_hash = md5_context.digest()
    if md5_hash:
        #print(f"MD5 Hash of '{input_file_path}': {md5_hash}")
        write_hash_to_file(output_file_path, md5_hash)

    return True

if __name__ == "__main__":
    main()

def main():
    if len(sys.argv) < 2:
        print("Please provide an input .toc file.")
        exit(1)

    input_file_path = sys.argv[1]
    process_file(input_file_path)