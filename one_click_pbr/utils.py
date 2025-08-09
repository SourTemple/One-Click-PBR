# one_click_pbr/utils.py
# Contains helper functions for finding files and resolving conflicts.

import os
import re

def find_texture_by_keywords(directory, file_list, keywords):
    """Scans a list of files for names matching keywords."""
    found_files = []
    pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    for filename in file_list:
        if pattern.search(filename):
            found_files.append(os.path.join(directory, filename))
    return found_files

def resolve_conflict(file_paths, strategy):
    """Resolves which file to use when multiple are found."""
    if not file_paths: return None
    if len(file_paths) == 1: return file_paths[0]
    best_file = file_paths[0]
    if strategy == 'normal':
        opengl_maps = [p for p in file_paths if 'opengl' in p.lower()]
        best_file = opengl_maps[0] if opengl_maps else max(file_paths, key=os.path.getsize)
    elif strategy == 'displacement':
        exr_maps = [p for p in file_paths if p.lower().endswith('.exr')]
        best_file = exr_maps[0] if exr_maps else max(file_paths, key=os.path.getsize)
    return best_file

def get_base_name_from_file(filename, keywords):
    """Gets a 'base name' from a texture file to identify unique sets."""
    for keyword in keywords:
        parts = re.split(keyword, filename, flags=re.IGNORECASE)
        if len(parts) > 1:
            return parts[0].strip('_.- ')
    return filename
