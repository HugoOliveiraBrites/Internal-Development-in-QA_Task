import os
import shutil
import time
import hashlib
import sys
import logging
from threading import Thread

thread_running = True # Global variable to control the thread

def setup_logger(log): # Function to setup the logger
    print(f'{log}')
    logger = logging.getLogger('sync_logger')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(os.path.join(log, 'sync.log'))
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger



def calculate_checksum(file_path): # Function to calculate checksum of a file
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)
    return sha256.hexdigest()

def folder_sync(source, replica): # Function to sync the source folder to the replica folder
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_path)

        if not os.path.exists(replica_root):
            os.makedirs(replica_root)
            logger.debug('Created directory %s', replica_root)

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(replica_file) or calculate_checksum(source_file) != calculate_checksum(replica_file):
                shutil.copy2(source_file, replica_file)
                logger.debug('Copied file %s to %s', source_file, replica_file)

    for root, dirs, files in os.walk(replica):
        relative_path = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                logger.debug('Removed file %s', replica_file)

        for dir in dirs:
            replica_dir = os.path.join(root, dir)
            source_dir = os.path.join(source_root, dir)

            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                logger.debug('Removed directory %s', replica_dir)

def folder_sync_thread(source, replica, interval): # Function to run the folder_sync function in a thread
    global thread_running
    logger.info('Syncing %s to %s every %s seconds', source, replica, interval)

    while thread_running:
        folder_sync(source, replica)
        time.sleep(interval)

def user_input(): # Function to take user input to stop the program
    while True:
        if  input('Enter "exit" to stop the program: \n') == 'exit':
            break
        else:
            print('Invalid input. Please enter "exit" to stop the program.')
            continue

if __name__ == "__main__":
    print('\******************************************************\\')
    print('Command Line Arguments: Program Name, Source Folder, Replica Folder, Time Interval, Log File Directory')
    print('\******************************************************\\ \n')

    if len(sys.argv) != 5:
        print('Invalid number of arguments. Exiting...')
        sys.exit()

    source = sys.argv[1] # Source folder path
    replica = sys.argv[2] # Replica folder path
    log = sys.argv[4] # Log file directory path
    interval = int(sys.argv[3]) # Time interval in seconds


    print('\******************************************************\\')
    print(f'Syncing {source} to {replica} every {interval} seconds.')
    print(f'Logging to {log}')
    print('******************************************************\\ \n')

    logger = setup_logger(log)

    t1 = Thread(target=folder_sync_thread, args=(source, replica, interval))
    t2 = Thread(target=user_input)

    t1.start()
    t2.start()  


    t2.join()
    thread_running = False


    print('Exiting...')
    sys.exit()