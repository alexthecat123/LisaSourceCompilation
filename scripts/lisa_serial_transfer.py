import serial
import sys
import time
import os

echo_timeout = 5 # How long to wait for an echo from the Lisa before printing a warning.
empty_echo_threshold = 5 # How many empty echoes we can receive before we ask the user to reboot the Lisa.
bar_length = 40 # Length of the progress bars on the status line.

# Paths that contain files that we don't need to send to the Lisa.
bad_paths = ['DICT', 'LISA_OS/APIN', 'LISA_OS/BUILD', 'LISA_OS/FONTS', 'LISA_OS/LIBHW', 'LISA_OS/Linkmaps 3.0', 'LISA_OS/Linkmaps and Misc. 3.0', 'LISA_OS/OS exec files', 'Lisa_Toolkit']
# Three files from within the "invalid" LISA_OS/BUILD directory that we actually do want to send.
valid_paths = ['BUILD/BUILD-COMP', 'BUILD/BUILD-ASSEMB', 'BUILD/BUILD-INSTALL']

path_list = [] # List of all the file paths to send.
name_list = [] # List of the corresponding filenames, in the format that we'll use on the Lisa.

size = 0 # Total size of all files to send, used for the total progress bar.
bytes_sent = 0 # Total bytes sent so far, used for the total progress bar.
total_files = 1 # Total number of files to send, used for the file counter.

# Converts seconds to a string in the format HH:MM:SS.
def hms(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02}"

# Converts seconds to a string in the format MM:SS.
def ms(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    secs = seconds % 60

    return f"{minutes:02}:{secs:02}"

# Prints a progress bar at the top of the screen, showing current file progress and total progress.
def print_progress_bar(filename, current_file, total_filecnt, current_char, total_chars, size, start_time):
    global bytes_sent
    file_percent = (current_char / total_chars) * 100 # Percentage of the current file that has been sent.
    file_filled_length = int(bar_length * current_char // total_chars) # Figure out how much of the progress bar to fill.
    file_bar = '█' * file_filled_length + '-' * (bar_length - file_filled_length) # And make a string representing the bar.

    total_percent = (bytes_sent / size) * 100 # Percentage of the total transfer that has been completed.
    total_filled_length = int(bar_length * bytes_sent // size) # Figure out how much of the total progress bar to fill.
    total_bar = '█' * total_filled_length + '-' * (bar_length - total_filled_length) # And make it.

    sys.stdout.write('\0337') # Save the current cursor position.
    sys.stdout.write('\033[1;1H') # Move the cursor to the top left of the terminal.
    sys.stdout.write('\033[2K') # And clear the line.

    if directory: # If we're sending a directory (multiple files), show current file progress and total progress.
        sys.stdout.write(f'Sending file {current_file}/{total_filecnt}: {filename} [{file_bar}] {file_percent:.2f}% Elapsed: {ms(time.time() - start_time)} ETA: {ms((time.time() - start_time) * (total_chars - current_char) / max(current_char, 1))} CPS: {(current_char / ((time.time() - start_time))):.1f}           Total Progress: [{total_bar}] {total_percent:.2f}% Elapsed: {hms(time.time() - global_start_time)} ETA: {hms((time.time() - global_start_time) * (size - bytes_sent) / max(bytes_sent, 1))}\r')
    else: # Otherwise, just show the current file progress.
        sys.stdout.write(f'Sending file {current_file}/{total_filecnt}: {filename} [{file_bar}] {file_percent:.2f}% Elapsed: {ms(time.time() - start_time)} ETA: {ms((time.time() - start_time) * (total_chars - current_char) / max(current_char, 1))} CPS: {(current_char / ((time.time() - start_time))):.1f}\r')
    
    sys.stdout.write('\0338') # Restore the cursor position to where it was before.
    sys.stdout.flush()

# Configures the Lisa to receive a file, and sends the file byte by byte.
def send_single_file(file_path, filename):
    global bytes_sent
    errors = 0 # The number of transmission errors (echoes that didn't match the sent byte).
    print('\n')
    print(f'Starting to send file {filename}...') # Tell the user what we're doing.
    print('\n')
    print_progress_bar(filename, total_files - len(path_list), total_files, 0, os.path.getsize(file_path), size, time.time()) # Initial progress bar.
    log_file.write(f'{filename} ({total_files - len(path_list)}/{total_files}): ') # Put the Lisa filename in the log file.
    log_file.flush()

    start_time = time.time() # Get the start time of the transfer.
    lisa.write(b'rcopy\r>' + filename.encode('mac-roman') + b'\r') # Tell the Lisa to r{un} the copy tool, giving it the Lisa-formatted filename that we want to save to.
    lisa.read(200) # Wait for the Lisa to catch up by reading some bytes.
    try:
        with open(file_path, 'rb') as source_file: # Now open the file we want to send.
            line_count = 1 # Line counter for error reporting.
            echo_counter = 0 # Number of empty echoes received, used to determine if we need to reboot the Lisa.
            prev_sent = bytes_sent # Previous bytes sent, used to to roll back the progress bar if we have to retry sending the file.
            while (byte := source_file.read(1)): # Read the file byte by byte.
                bytes_sent += 1 # And increment the total bytes sent; used for the total progress bar.
                if byte == b'\xFF': # Each file has a garbage FF byte at the end, which we don't want to send.
                    break
                if byte == b'\r': # Check for \r\n line endings, and convert them to just \r.
                    byte = source_file.read(1) # Read the next byte to see if it's a \n.
                    if byte != b'\n': # If it's not a \n, we need to rewind the file by one byte, so we can send the \r again.
                        source_file.seek(-1, os.SEEK_CUR)
                    else: # If it is a \n, we can just continue.
                        bytes_sent += 1
                        byte = b'\r'
                if byte == b'\n': # The Lisa expects \r line endings, so convert all \n's to \r's.
                    byte = b'\r'
                if byte == b'\r': # If we encounter a \r, increment the line count.
                    line_count += 1
                lisa.write(byte) # And now send the byte to the Lisa.
                echo = lisa.read() # Read the echoed byte from the Lisa.
                timeout_start = time.time() # And start a timer to see if we get an echo back in time.
                while echo != byte: # If the echoed byte doesn't match the sent byte, keep reading until it does.
                    echo = lisa.read()
                    if time.time() - timeout_start > echo_timeout: # If the echo doesn't match after the timeout, we might have a problem.
                        if not echo and byte.decode('mac-roman').isprintable(): # If the echo is empty (for a printable byte that we expect to get an echo from), the Lisa probably needs a reboot.
                            echo_counter += 1 # Increment the empty echo counter.
                            if echo_counter < empty_echo_threshold: # If we get too many empty echoes, make the user reboot, else try again.
                                print('\n')
                                print(f'No echo received from the Lisa, retry #{echo_counter} of {empty_echo_threshold}.')
                                break
                            print('\n')
                            input('ERROR: The Lisa did not respond with an echo! Go ahead and reboot it, run the EXEC file ALEX/TRANSFER.TEXT again, and hit RETURN on this computer to try sending this file again...')
                            print('\n')
                            log_file.write('\nERROR: The Lisa did not respond with an echo! Retrying transfer after reboot...')
                            log_file.flush()
                            errors = 0 # Reset all our transfer variables.
                            echo_counter = 0
                            line_count = 1
                            bytes_sent = prev_sent
                            source_file.seek(0) # And rewind the file to the beginning.
                            log_file.write(f'\n{filename} Again ({total_files - len(path_list)}/{total_files}): ') # Put the filename in the logfile again.
                            log_file.flush()
                            lisa.write(b'qqn')
                            lisa.read(200) # Wait for the Lisa to catch up again.
                            lisa.write(b'rcopy\r>' + filename.encode('mac-roman') + b'\r') # Tell the Lisa to r{un} the copy tool, giving it the Lisa-formatted filename that we want to save to.
                            lisa.read(200) # Wait for the Lisa to catch up by reading some bytes.
                            break
                        elif echo or (not echo and not byte.decode('mac-roman').isprintable()): # If we got an echo, but it doesn't match the sent byte, or we don't get an echo for a non-printable byte, we might have a mismatch.
                            errors += 1 # Increment the error count.
                            print('\n')
                            # And show the user a warning message.
                            print(f'WARNING: Echo was supposed to be "{byte.decode("mac-roman") if byte != b'\r' and byte != '\n' else '[newline]'}", but was actually "{echo.decode("mac-roman") if echo != b'\r' and echo != '\n' else '[newline]'}" on line {line_count}.')
                            if not byte.decode('mac-roman').isprintable(): # If the byte isn't printable, then it might not be a problem.
                                print('This happened on an unprintable character, so it might not be a problem.')
                            print('\n')
                            # Log it to the log file too.
                            log_file.write(f'\nWARNING: Echo was supposed to be "{byte.decode("mac-roman") if byte != b'\r' and byte != '\n' else '[newline]'}", but was actually "{echo.decode("mac-roman") if echo != b'\r' and echo != '\n' else '[newline]'}" on line {line_count}. ')
                            if not byte.decode('mac-roman').isprintable(): # If the byte isn't printable, then it might not be a problem.
                                log_file.write('This happened on an unprintable character, so it might not be a problem. ')
                            log_file.flush()
                            break

                # Update the progress bar after each byte is sent.
                print_progress_bar(filename, total_files - len(path_list), total_files, source_file.tell(), os.path.getsize(file_path), size, start_time)
                # And print the echoed byte to the terminal so the user can see what's going on.
                print(echo.decode('mac-roman') if echo != b'\r' else '\n', end='')

        lisa.read(200) # Wait for the Lisa to catch up again.

    except KeyboardInterrupt: # If the user interrupts the transfer, we need to make sure that they have control over the Lisa again.
        print('\n')
        print('Transfer interrupted by user. Returning control to the Lisa...')
        lisa.read(200) # Wait for the Lisa to catch up.
        lisa.write(b'\x0E\x0D\x0D') # Send the end-of-file sequence to the Lisa.
        lisa.read(200) # Wait for the Lisa to catch up again.
        lisa.write(b'scmy') # Return control of the Lisa to the user by doing a s{ystem-mgr}c{onsole}m{ain}y{es}.
        lisa.read(200) # And give it some time to process things.
        lisa.close() # Close the serial port.
        sys.exit(0)

    lisa.write(b'\x0E\x0D\x0D') # And then send the end-of-file sequence to the Lisa.
    lisa.read(200) # Wait again...
    print('\n')
    # And print a success message to the terminal.
    print(f'Finished sending file {filename}. Transmission took {ms(time.time() - start_time)} with {errors} error(s).')
    # Make sure the progress bar stays on the screen.
    print_progress_bar(filename, total_files - len(path_list), total_files, os.path.getsize(file_path), os.path.getsize(file_path), size, start_time)
    log_file.write(f'Finished in {ms(time.time() - start_time)}.\n') # And write the success to the log file too.
    log_file.flush()

if len(sys.argv) != 3: # Make sure the user provided both a serial port and a file or directory to transmit.
    print(f'Usage: python3 {sys.argv[0]} <serial_port> <directory_or_file_to_send>')
    print(f'Example: python3 {sys.argv[0]} /dev/ttyUSB0 Lisa_Source')
    sys.exit(1)

file_or_dir = sys.argv[2] # The file or directory to send to the Lisa.

if os.path.isdir(file_or_dir): # Check if the user wants to send a directory.
    directory = True # If so, set a flag.
    for root, dir, files in os.walk(file_or_dir): # And walk through the directory and its subdirectories.
        for file_name in files: # For each file in the directory...
            # Check if it's a .UNIX.TXT or .TEXT file. These are the only files we want to send.
            if(file_name.lower().endswith('.unix.txt') or file_name.lower().endswith('.text')):
                # Convert the filename to the Lisa format, replacing .UNIX.TXT with .TEXT and converting dots and dashes to slashes.
                new_file_name = file_name.upper().replace('.UNIX.TXT', '').replace('.', '/').replace('-', '/')
                new_file_name = new_file_name.replace('/TEXT', '.TEXT')
                full_path = os.path.abspath(os.path.join(root, file_name)) # Get the full path of the file too.
                # Check if the file is in a bad path (the path lists we defined at the top). And skip it if so.
                if any(bad_path in full_path for bad_path in bad_paths) and not any(valid_path in full_path for valid_path in valid_paths):
                    continue
                else:
                    size += os.path.getsize(full_path) # If the file is valid, add its size to the total transfer size.
                    path_list.append(full_path) # And append its full path and Lisa-formatted name to the path and name lists.
                    name_list.append(new_file_name)
    total_files = len(path_list) # Set the total number of files to send to the length of the path list.
    
else: # If we're here, the user provided a single file to send.
    directory = False # So clear the directory flag.
    size = 1 # Avoid division by zero errors later on.
    # And once again, make sure it's a .UNIX.TXT or .TEXT file.
    if(file_or_dir.lower().endswith('.unix.txt') or file_or_dir.lower().endswith('.text')):
        # Do the same conversion to the Lisa filename as above, and add it to the path and name lists.
        new_file_name = os.path.split(file_or_dir)[-1]
        new_file_name = new_file_name.upper().replace('.UNIX.TXT', '').replace('.', '/').replace('-', '/')
        new_file_name = new_file_name.replace('/TEXT', '.TEXT')
        path_list.append(file_or_dir) # Lists will only one item this time!
        name_list.append(new_file_name)
    else: # We end up here and exit if the file isn't a .UNIX.TXT or .TEXT file.
        print(f'Error: {file_or_dir} is not a .TEXT or .UNIX.TXT file!')
        sys.exit(1)

# ----------------------------------------------- Start of main program!!! -----------------------------------------------

sys.stdout.write('\033[2J') # Clear the terminal screen.
sys.stdout.flush()

# Make sure the Lisa is ready to receive files by prompting the user.
input('Run the EXEC file ALEX/TRANSFER.TEXT on your Lisa, and hit RETURN on this computer once the Lisa screen goes blank...')

try: # Attempt to connect to the Lisa over serial, and exit with an error if we fail.
    lisa = serial.Serial(port=sys.argv[1], baudrate=28800, bytesize=8, dsrdtr=True, timeout=1)
except:
    print(f'Error: Failed to open serial port {sys.argv[1]}!')
    sys.exit(1)

lisa.read(200) # The Lisa might send us some stuff when we connect, so read it to clear the buffer.
# To get into a known state, send the Lisa a q{uit}q{uit}n{o, don't exit the shell}. Regardless of where we are, this should get us to the main Workshop screen.
lisa.write(b'qqn')
lisa.read(200) # Wait for the Lisa to catch up again.

log_file = open('log.txt', 'w') # Open our log file for writing.
log_file.write(f'About to transmit {total_files} file(s).\n') # And write the total number of files to send.
log_file.write(f'Starting at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.\n') # As well as the start time.
log_file.flush()

global_start_time = time.time() # Get the global start time for the entire transmission.

if directory: # If we're sending a directory, we need to send each file in the path list.
    while path_list: # So iterate through it and pop a name and path off on each iteration.
        path = path_list.pop(0)
        name = name_list.pop(0)
        send_single_file(path, name) # Now we just need to send the file we popped off!
    # We're done now, so say so in the log file and print a message to the terminal.
    log_file.write(f'Finished sending all files. Full transmission took {hms(time.time() - global_start_time)}.\n')
    print(f'Finished sending all files. Full transmission took {hms(time.time() - global_start_time)}.')

else: # We're sending a single file, so we can just send it directly without any looping.
    send_single_file(path_list.pop(0), name_list.pop(0))

# Close out the log file with the end time.
log_file.write(f'Ending at {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}.\n')
log_file.close()

lisa.write(b'scmy') # Return control of the Lisa to the user by doing a s{ystem-mgr}c{onsole}m{ain}y{es}.
lisa.read(200) # And give it some time to process things.
print('All done, you should have control over your Lisa again!') # And now we're done!!!
print()
lisa.close()