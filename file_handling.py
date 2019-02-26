import os
#os.chdir(r'C:\Users\A.Kunikoshi\source\repos\toolbox\toolbox')
import glob
import shutil


def make_filelist(dir_target, file_txt, file_type='*'):
    """make a list of files in the directory. 

	Args:
		dir_target (path): the directory of which a list of files will be output.
		file_txt (path): the text file in which a list of files in dir_target will be written.
		file_type (string): filetype. default is * (all). 

    """
    #listdir = os.listdir(dir_target)
    listdir = glob.glob(os.path.join(dir_target, '*.' + file_type))

    with open(file_txt, 'wt') as f:
        f.write('\n'.join(listdir))

    return


def make_new_directory(directory, existing_dir='delete'):
	"""make new directory. 

	Args:
		directory (path):
		(existing_dir) ('delete' or 'leave'): if the directory already exist, what to do. default is 'delete'.

	"""
	if os.path.exists(directory):
		if existing_dir == 'delete':
			shutil.rmtree(directory)
			os.makedirs(directory)
	else:
		os.makedirs(directory)


if __name__ == 'main':
    dir_target = r'C:\Aki\htk\data\test'
    file_txt   = r'C:\Aki\htk\config\test.txt'

    make_filelist(dir_target, file_txt)