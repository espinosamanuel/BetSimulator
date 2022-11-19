import os
import shutil

base_path = os.path.dirname(__file__)
input_path = os.path.join(base_path, '../input')
tmp_path = os.path.join(base_path, '../tmp')
data_path = os.path.join(base_path, '../data')
output_path = os.path.join(base_path, '../output')

odds_columns = ['H', 'D', 'A']


def replace_directory(dir_path):
    """Deletes the given directory and all its files and subdirectories.
    Then creates a new directory with the same path.
    """
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

    os.mkdir(dir_path)


def create_directory(dir_path):
    """Creates a directory if the given path not exists"""
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
