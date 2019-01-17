import os

dir_main = r'C:\Aki\htk'

dir_config = os.path.join(dir_main, 'config')
HCompV_scp = os.path.join(dir_config, 'HCompV.scp')
config_train = os.path.join(dir_config, 'config.train')
#set phaselist_txt=%dirConfig%\phaselist.txt
#set plMkhmmdefs=%dirConfig%\mkhmmdefs.pl

dir_data = os.path.join(dir_main, 'data')
dir_train = os.path.join(dir_data, 'train')

dir_model  = os.path.join(dir_main, 'model')
dir_model0 = os.path.join(dir_model, 'hmm0')
name_proto   = 'proto'
name_hmmdefs = 'hmmdefs'
