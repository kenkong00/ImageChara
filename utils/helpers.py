import os
import re
import datetime


def shorten_filename(filename, max_length=30):
    if len(filename) <= max_length:
        return filename
    
    name, ext = os.path.splitext(filename)
    available_length = max_length - len(ext) - 3
    
    if available_length <= 0:
        return "..." + ext
    
    shortened_name = name[:available_length] + "..."
    return shortened_name + ext


def parse_dropped_files(file_paths):
    if not isinstance(file_paths, str):
        return []
    
    paths = []
    brace_pattern = r'\{([^}]+)\}'
    brace_matches = re.findall(brace_pattern, file_paths)
    
    if brace_matches:
        paths = brace_matches
    elif '"' in file_paths:
        pattern = r'"([^"]+)"'
        paths = re.findall(pattern, file_paths)
    else:
        paths = [file_paths.strip()]
    
    image_paths = []
    for path in paths:
        path = path.strip()
        if path.lower().endswith(('.png', '.webp', '.jpg', '.jpeg')):
            image_paths.append(path)
    
    return image_paths


def get_timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")
