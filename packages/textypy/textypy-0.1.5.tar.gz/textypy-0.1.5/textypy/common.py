import os

def in_data_dir(fpath):
    this_path = os.path.dirname(os.path.realpath(__file__))    
    data_path = os.path.join(this_path, 'data')
    return os.path.join(data_path, fpath)
