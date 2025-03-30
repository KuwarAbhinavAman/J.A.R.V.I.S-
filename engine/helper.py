import os
import re
import time


def extract_yt_term(command):
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None


def remove_words(input_string, words_to_remove):
    """Improved word removal with regex for better handling"""
    pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, words_to_remove)))
    return re.sub(pattern, '', input_string, flags=re.IGNORECASE).strip()


