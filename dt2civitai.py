#!/opt/homebrew/bin/python3
"""
dt2civitai.py
Version 0.6
Author: Zanshinmu
Email: zanshin.g1+dt2civ@gmail.com
Date: 2024-03-17
Description: This script provides processing of Draw Things created PNG files metadata into A1111 compatible format for Civitai, writing it to new PNGs.
"""
import json
import sys
import glob
import os
import hashlib
import shutil
import subprocess
import secrets
from functools import lru_cache
from pathlib import Path
from PIL import Image
from PIL.PngImagePlugin import PngInfo

# default Draw Things Model Directory
DT_MODEL_DIRECTORY = Path.home() / "Library/Containers/com.liuliu.draw-things/Data/Documents/models/"

''' If you use an external model directory in Draw Things:
    uncomment the next line and change to external model directory path
'''
# DT_MODEL_DIRECTORY = "/External/Model/Directory/path/here/"

# Set the Modified File Suffix
MODIFIED_SUFFIX = "_civ"

# We will populate this later from args
DESTINATION_DIRECTORY = None

# Hash function, now with extra cache
@lru_cache
def hash_file(filename, length=32):
    sha256_hash = hashlib.sha256()
    if not os.path.exists(filename):
        sha256_hash.update(str(filename).encode('utf-8'))
        #Using the model filename to fake hash
    else:
        """Generate SHA-256 hash of the contents of a file."""
        with open(filename, "rb") as f:  # Open the file in binary mode
        # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()[:length]
    
def extract_format_and_embed_metadata(png_path):
    # Extract UserComment metadata as JSON
    user_comment_result = subprocess.run(['exiftool', '-UserComment', '-b', '-json', png_path], capture_output=True, text=True)
    # If we can't read UserComment it's not a valid file, abort
    try:
        user_comment_data = json.loads(user_comment_result.stdout)[0]['UserComment']
    except KeyError:
        return False
        
    user_comment_data = json.loads(user_comment_data)

    # Extracting 'model' directly and from 'lora', removing '.ckpt' from the ends if present
    modelfile=user_comment_data.get('model', '')
    direct_model = modelfile.rstrip('.ckpt')
    lora_model = user_comment_data['lora'][0].get('model', '').rstrip('.ckpt') if 'lora' in user_comment_data and user_comment_data['lora'] else None

    # Extract "MD Item Creator" field
    md_item_creator_result = subprocess.run(['exiftool', '-MDItemCreator', '-b', png_path], capture_output=True, text=True)
    md_item_creator = md_item_creator_result.stdout.strip()
    
    # Compute hash of model file
    # Civitai expects a hash length of 10
    model_hash=hash_file(DT_MODEL_DIRECTORY / modelfile, 10)
    
    # Hi-Res Fix?
    hires_fix = user_comment_data.get('hires_fix', '')
    # use different value depending on hires_fix
    #size = None
    if hires_fix:
        size = user_comment_data.get('first_stage_size', '')
    else:
        size = user_comment_data.get('original_size', '')
        

    # Formatting the metadata
    formatted_data_str = ""
    if lora_model is not None:
        formatted_data_str += f"<lora:{lora_model}:1>,, "
        
    formatted_data_str += (
        f"{user_comment_data.get('c', '')}\n"
        f"Negative prompt: {user_comment_data.get('uc', '')}\n"
        f"Steps: {user_comment_data.get('steps', '')}, "
        f"Sampler: {user_comment_data.get('sampler', '')}, "
        f"CFG scale: {user_comment_data.get('scale', '')}, "
        f"Seed: {user_comment_data.get('seed', '')}, "
        f"Size: {size}, "
        f"Model hash: {model_hash}, "
        f"Model: {direct_model}, "
    )
    # Hi-Res Fix
    if hires_fix:
        formatted_data_str += (
            f"Denoising strength: {user_comment_data.get('second_stage_strength', '')}, "
            f"Hires resize: {user_comment_data.get('original_size', '')}, "
        )
    # Insert MD Item Creator as "Version", maybe liu liu will add a version string?
    formatted_data_str +=f"Version: {md_item_creator}"
    
    # Embed the formatted metadata into the 'Parameters' tag of the new PNG file
    # pillow will strip the metadata and create a new file with the new extension
    add_png_text_tag(png_path, "parameters", formatted_data_str)
    return True
    
def modify_filename(path, addition):
    """
    Adds characters to a filename before its extension.
    
    :param path: The original file path
    :param addition: The string to add before the file extension
    :return: New file path with added characters before the extension
    """
    dirname = os.path.dirname(path)  # Get the directory name
    basename = os.path.basename(path)  # Get the base file name
    name, ext = os.path.splitext(basename)  # Split the base name and extension
    
    # Create a new filename with the addition before the extension
    new_filename = f"{name}{addition}{ext}"
    #Delete if it exists
    if os.path.exists(new_filename):
        os.remove(new_filename)
    return os.path.join(dirname, new_filename)

# pillow can be used to copy file and strip metadata, reducing dependence
# on exiftool
def add_png_text_tag(image_path, tag_name, tag_value):
    # Open the target image
    target = Image.open(image_path)
    # Pillow's img.info dictionary contains the metadata for PNG images.
    # Create a new PngInfo object to hold our modified metadata.
    newinfo = PngInfo()
    newinfo.add_text(tag_name, tag_value)
    # The correct way to save the image with new metadata is to use the pnginfo parameter.
    # We save the image to a new path to avoid any potential issues with reading and writing to the same file simultaneously.
    if DESTINATION_DIRECTORY is not None:
        save_dir = create_dest_directory(DESTINATION_DIRECTORY)
        save_file = os.path.basename(modify_filename(image_path, MODIFIED_SUFFIX))
        new_path = save_dir / save_file
    else:
        new_path = modify_filename(image_path, MODIFIED_SUFFIX)
        
    target.save(new_path, pnginfo=newinfo)
    
# Process files and directories from arguments
def process_files(file_paths):
    for png_path in file_paths:
        basename = os.path.basename(png_path)
        if extract_format_and_embed_metadata(png_path):
            print(f"processed {basename}\n")
        else:
            print(f"{basename}: no Draw Things metadata found!\n")
    #print(hash_file.cache_info())

def create_dest_directory(dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Destination directory '{dest_dir}' created.\n")
        
    return Path(dest_dir)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        DESTINATION_DIRECTORY = sys.argv[2]
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            png_files = glob.glob(os.path.join(path, '*.png'))
            process_files(png_files)
        elif os.path.isfile(path) and path.lower().endswith('.png'):
            process_files([path])
        else:
            print("The provided path is not a directory or a PNG file.")
    else:
        png_files = glob.glob('*.png')
        process_files(png_files)
