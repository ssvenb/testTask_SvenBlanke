import os
import shutil
import filecmp
import time
import sys
import getopt

def log_to_console_and_file(statement):
    # log operations to console and log_file
    print(statement)
    with open(path_log_file, 'a') as file:
        file.write(statement + '\n')

def remove_files(path_replica, file):
    '''
    Removal of Files and Directories if they were removed in the source folder
    '''
    
    # path of the file will be deleted in the replica folder
    path_copy = os.path.join(path_replica, file)
    try:
        # deleting all files in the folder
        os.remove(path_copy)
        statement = 'File ' + path_copy + ' removed'
        log_to_console_and_file(statement)
    except PermissionError:
        try:
            # if there is a folder in the directory remove it if it's empty
            os.rmdir(path_copy)
            statement = 'Directory ' + path_copy + ' removed'
            log_to_console_and_file(statement)
        except:
            # if the folder is not empty remove all files and folders inside it
            files_replica = os.listdir(path_copy)
            for file in files_replica:
                # call the remove_files function again for all folders and files inside the folder
                remove_files(path_replica=path_copy,
                             file=file)
            os.rmdir(path_copy)
            statement = 'Directory ' + path_copy + ' removed'
            log_to_console_and_file(statement)

def synchronize(path_source, path_replica):
    '''
    Synchronization of Files and Directories
    If a File has been added or modified it gets replaced in the replica Folder
    '''
    
    files_source = os.listdir(path_source)
    files_replica = os.listdir(path_replica)
    
    # Iterate through all files in the replica folder and delete those that are not in the source folder
    for file in files_replica:
        if file not in files_source:
            remove_files(path_replica=path_replica,
                         file=file)
    
    # Iterate through all the files in the source folder
    for file in files_source:
        
        try:
            # paths to the source and replica folder
            path_file = os.path.join(path_source, file)
            path_copy = os.path.join(path_replica, file)
            
            if file not in files_replica:
                # copy new files to the replica folder
                shutil.copyfile(path_file, path_copy)
                statement = 'File ' + path_copy + ' copied'
                log_to_console_and_file(statement)
                
            else:
                # check if folders are identical
                identical = filecmp.cmp(path_file, path_copy)                       
                if not identical:
                    # if the file in the source folder has been modified replace file in the replica folder
                    os.remove(path_copy)
                    shutil.copyfile(path_file, path_copy)
                    statement = 'File ' + path_copy + ' modified'
                    log_to_console_and_file(statement)
                    
        except PermissionError:
            # if a folder is in the directory check if it has been copied to the replica folder
            if not os.path.exists(path_copy):
                # if the folder is new copy it to the replica folder
                os.mkdir(path_copy)
                statement = 'Directory ' + path_copy + ' created'
                log_to_console_and_file(statement)
            # call the synchronize function on the file path of the folder in the source folder
            synchronize(path_source=path_file,
                        path_replica=path_copy)
            

if __name__ == '__main__':
    '''
    Run program with: 
    python sync.py -s <path source> -r <path replica> -l <path logfile> -i <synchronization interval>
    
    The program keeps running until it's stopped.
    While it's running it synchronizes all the files of the source folder to the replica folder
    once per synchronization interval.
    '''
    
    # paths to the source and replica folder
    path_dir = os.path.dirname(os.path.abspath(__file__))
    
    # default paths and synchronization interval
    path_source = os.path.join(path_dir, 'source')
    path_replica = os.path.join(path_dir, 'replica')
    path_log_file = os.path.join(path_dir, 'log_file.txt')
    synchronization_interval = 1
    
    # command line arguments
    opts, args = getopt.getopt(sys.argv[1:], 's:r:l:i', ['path_source', 'path_replica', 'path_log_file', 'synchronization_interval'])
    
    # define command line options
    for opt, arg in opts:
        if opt == '-s':
            path_source = arg
        if opt == '-r':
            path_replica = arg
        if opt == '-l':
            path_log_file = arg
        if opt == '-i':
            synchronization_interval = arg
    
    while True:

        # Synchronize all files of the source folder to the replica folder
        synchronize(path_source=path_source,
                    path_replica=path_replica)
        
        # wait for synchronization interval
        time.sleep(synchronization_interval)
