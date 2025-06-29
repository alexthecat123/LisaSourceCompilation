import os
for root, dirs, files in os.walk('.'):
    for file_name in files:
        if file_name.lower().endswith('.unix.txt'):
            file_path = os.path.join(root, file_name)
            try:
                with open(file_path, 'r', encoding='iso-8859-1') as file:
                    contents = file.read()
                
                lines = contents.splitlines()
                final_contents = '\r'.join(lines[:-1]) + '\r'

                os.remove(file_path)
                
                with open(file_path.split('.unix.txt')[0], 'w', encoding='iso-8859-1') as file:
                    print('writing ', file_path.split('.unix.txt')[0])
                    file.write(final_contents)
                
            except Exception as e:
                print(f"Failed on file {file_path}: {e}")