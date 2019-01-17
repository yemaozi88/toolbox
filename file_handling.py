import os
os.chdir(r'C:\Users\A.Kunikoshi\source\repos\toolbox\toolbox')
import glob

def make_filelist(dir_target, file_txt, file_type='*'):
    """
    make a list of files in the directory. 
    :param path dir_target: the directory of which a list of files will be output.
    :param path file_txt: the text file in which a list of files in dir_target will be written.
    :param string file_type: filetype. default is * (all). 
    """
    #listdir = os.listdir(dir_target)
    listdir = glob.glob(os.path.join(dir_target, '*.' + file_type))

    with open(file_txt, 'wt') as f:
        f.write('\n'.join(listdir))

    return


if __name__ == 'main':
    dir_target = r'C:\Aki\htk\data\test'
    file_txt   = r'C:\Aki\htk\config\test.txt'

    make_filelist(dir_target, file_txt)