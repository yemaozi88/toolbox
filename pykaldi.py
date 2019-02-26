"""
The module to use Kaldi.
"""
import sys
import os
os.chdir(r'C:\Users\Aki\source\repos\toolbox')
#from subprocess import Popen, PIPE
#import re
#from tempfile import NamedTemporaryFile
#import shutil

import numpy as np
import pandas as pd

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#import file_handling as fh
#from scripts import run_command, run_command_with_output


#def read_ctm(ctm_file):
ctm_file = r'C:\OneDrive\WSL\kaldi-trunk\egs\_stimmen\exp\mono\result.txt'
phone_txt = r'C:\OneDrive\WSL\kaldi-trunk\egs\_stimmen\data\lang\phones.txt'
phone_ids = pd.read_csv(phone_txt, delimiter=' ', header=None, encoding="utf-8")
phone_ids.rename(columns={0: 'phone', 1: 'phone_id'}, inplace=True)
translation_key = dict()
for index, row in phone_ids.iterrows():
	#print('{0} --> {1}'.format(row['phone_id'], row['phone']))
	translation_key[row['phone_id']] = row['phone']

ctm = pd.read_csv(ctm_file, delimiter=' ', header=None, encoding="utf-8")
ctm.rename(columns={0: 'utt_id', 1: 'channel_num', 2: 'start_time', 3: 'phone_dur', 4: 'phone_id'}, inplace=True)

utt_id_list = list(np.unique(ctm['utt_id']))
utt_id = utt_id_list[10]
ctm_ = ctm[ctm['utt_id'].str.match(utt_id)]

phones = [translation_key.get(i, i) for i in ctm_['phone_id']]
' '.join(phones).replace('_S', '').replace('_B', '').replace('_E', '')	