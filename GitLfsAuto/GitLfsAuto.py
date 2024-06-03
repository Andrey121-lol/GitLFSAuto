# -*- coding: utf-8 -*-
import os
import subprocess
import gitignore_parser
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to find large files in a directory and its subdirectories
def find_large_files(directory, size_limit):
    gitignore_path = os.path.join(directory, '.gitignore')
    if os.path.exists(gitignore_path):
        matches = gitignore_parser.parse_gitignore(gitignore_path)
    else:
        matches = lambda x: False
    
    large_files = []
    for root, dirs, files in os.walk(directory):
        # Skip .git directory and ignored directories
        dirs[:] = [d for d in dirs if d != '.git' and not matches(os.path.relpath(os.path.join(root, d), directory))]
        
        for file in files:
            file_path = os.path.join(root, file)
            # Skip ignored files
            if matches(os.path.relpath(file_path, directory)):
                continue
            if os.path.getsize(file_path) > size_limit:
                large_files.append(os.path.relpath(file_path, directory))
    return large_files

# Function to check if Git LFS is installed
def check_and_install_git_lfs():
    try:
        # Check if Git LFS is installed by running `git lfs version`
        subprocess.run(['git', 'lfs', 'version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.debug("Git LFS is already installed.")
    except subprocess.CalledProcessError:
        # If Git LFS is not installed, run `git lfs install`
        logging.debug("Git LFS is not installed. Installing Git LFS...")
        try:
            subprocess.run(['git', 'lfs', 'install'], check=True)
            logging.debug("Git LFS has been successfully installed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Git LFS: {e}")
            raise

# Function to add files to Git LFS
def add_to_git_lfs(files):
    for file in files:
        subprocess.run(['git', 'lfs', 'track', file], check=True)
        subprocess.run(['git', 'add', file], check=True)
        logging.debug(f"Added to Git LFS: {file}")  # Log each file added to Git LFS
    logging.info(f"Total files added to Git LFS: {len(files)}")  # Log the total number of files added

# Main function
def main():
    try:
        directory = os.getcwd()  # Use current working directory
        logging.debug(f"Current working directory: {directory}")
        print(f"Current working directory: {directory}")

        check_and_install_git_lfs()  # Check and install Git LFS if necessary

        size_limit = 100 * 1024 * 1024  # 100 megabytes in bytes
        large_files = find_large_files(directory, size_limit)
        
        if large_files:
            print("Found large files:")
            for file in large_files:
                print(file)
                logging.debug(f"Found large file: {file}")  # Log each large file found
            add_to_git_lfs(large_files)
            print("Files have been added to Git LFS.")
        else:
            print("No large files found.")
            logging.info("No large files found.")
    except Exception as e:
        logging.exception("An error occurred")

    input("Press Enter to close the program...")

if __name__ == "__main__":
    main()
