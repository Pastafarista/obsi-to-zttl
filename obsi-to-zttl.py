#!/usr/bin/python3
# Description: Rename notes of obsidian to zettelkasten naming convention
# Author: Antonio Cabrera

import os
import sys
import re

def rename_note(note_path):
    ext = note_path.split('.')[-1]
    name = note_path.split('/')[-1].split('.')[0]
    path = '/'.join(note_path.split('/')[:-1])
    
    # Check if the file is a markdown file
    if ext != 'md':
        print(f'Error: {note_path} is not a markdown file')
        return

    # Get metadata of date of creation
    date = str(os.path.getctime(note_path)).split('.')[0]

    # Get the content of the note
    with open(note_path, 'r') as f:
        content = f.read()

    # Convert the name to zettelkasten naming convention
    id = name_to_zettelkasten(name, date)

    # Write the metadata to the note
    with open(note_path, 'w') as f:
        f.write(f'---\n')
        f.write(f'id: {id}\n')
        f.write(f'aliases:\n - {name}\n')
        f.write(f'---\n\n')
        f.write(content)
        f.close()

    # Rename the note
    new_note_path = f'{path}/{id}.md'
    os.rename(note_path, new_note_path)

    # Return the old and new name
    return name, id

# Convert the name of the note to zettelkasten naming convention
def name_to_zettelkasten(name, date):
    # Replace '_' with '-'
    name = name.replace('_', ' ')
    name = name.replace('-', ' ')

    # Remove special characters and spaces
    cleaned_name = re.sub(r'[^a-zA-Z0-9 ]', '', name)

    # Convert text to lowecase
    cleaned_name = cleaned_name.lower()
    
    # Replace spaces with underscores
    cleaned_name = cleaned_name.replace(' ', '-')
    
    # Combine the unique identifier and cleaned name
    zettelkasten_name = f"{date}-{cleaned_name}"
    
    return zettelkasten_name

def check_zettelkasten(name):
    # Define the pattern for the custom naming convention
    pattern = r'^\d{10}-[a-zA-Z0-9-]+$'
    
    # Check if the name matches the custom naming convention
    if re.match(pattern, name):
        return True
    else:
        return False
    
def update_links_vault(vault_path, cache_file):
    # Create rename table
    rename_table = {}

    # Open the cache file
    cache_file = open(cache_file, 'r')

    # Read the cache file
    for line in cache_file:
        old_name, new_name = line.split(' -> ')

        # Remove '\n' from new_name
        rename_table[old_name] = new_name.strip()

    # Close the cache file
    cache_file.close()

    # Go through the vault and update the links
    for root, _, files in os.walk(vault_path):
        for file in files:
            ext = file.split('.')[-1]
            file_name = file.split('/')[-1].split('.')[0]
            file_path = os.path.join(root, file)
            
            if ext == 'md' and file_name in rename_table.values():
                # Check if file contains the word 'excalidraw'
                if not re.match(r'.*excalidraw.*', file):
                    name = file.split('.')[0]
                    
                    print(f'Updating links in {file}')
                    
                    # Read the note
                    with open(file_path, 'r') as f:
                        content = f.read()
                        f.close()
                    
                    # Update links
                    for old_name, new_name in rename_table.items():
                        # Replace [[old_name]] -> [[new_name]
                        pattern = r'\[\[{}\]\]'.format(re.escape(old_name))

                        # Remove alias ([[old_name|alias]] -> [[new_name|alias]])
                        pattern_alias = r'\[\[{}\|([^]]+)\]\]'.format(re.escape(old_name))

                        # Update the content
                        content = re.sub(pattern, '[[{}|{}]]'.format(new_name, old_name), content, flags=re.IGNORECASE)
                        content = re.sub(pattern_alias, '[[{}|\\1]]'.format(new_name), content, flags=re.IGNORECASE)
                        
                    # Write the updated note
                    with open(file_path, 'w') as f:
                        f.write(content)
                        f.close()
                    
def rename_vault(vault_path):
    # Open the cache file
    cache_file = open('rename_cache.txt', 'a')
     
    for root, _, files in os.walk(vault_path):
        for file in files:
            ext = file.split('.')[-1]
            
            if ext == 'md':
                # Check if file contains the word 'excalidraw'
                if not re.match(r'.*excalidraw.*', file):
                    name = file.split('.')[0]

                    if not check_zettelkasten(name):
                        print(f'Renaming {file}')
                       
                        # Get the path of the note
                        note_path = os.path.join(root, file)

                        # Rename the note
                        old_name, new_name = rename_note(note_path)

                        # Write the rename in cache file
                        cache_file.write(f'{old_name} -> {new_name}\n')

    # Close the cache file
    cache_file.close()

if __name__ == '__main__':
    # Get vault path from argument
    vault_path = sys.argv[1]

    # If not argument is given, print usage
    if vault_path == '':
        print('Usage: obsi-to-zttl.py <vault_path>')
        exit(1)

    print(f'Renaming notes in {vault_path}')
    rename_vault(vault_path)
    print(f'Updating links in {vault_path}')
    update_links_vault(vault_path, 'rename_cache.txt')

