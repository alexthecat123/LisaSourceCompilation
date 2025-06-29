import os
import sys

if len(sys.argv) < 2:
    print("Usage: python3 singlefile_cr.py <file>")
    sys.exit()
    
file_path = sys.argv[1]
try:
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        contents = file.read()
    
    new_contents = contents.replace('\n', '\r')
    
    with open(file_path, 'w', encoding='iso-8859-1') as file: # previously said encoding was utf-8
        file.write(new_contents)
        print('all done!')
    
except Exception as e:
    print(f"Failed for reason: {e}")
