"""
The module to train HMM (Hidden Markov Model) for Sit-to-Stand test phase detection.
"""
import sys
import os
os.chdir(r'C:\Users\A.Kunikoshi\source\repos\toolbox\toolbox')

import defaultfiles as default
import file_handling as fh
import pyhtk


# list of feature files.
fh.make_filelist(default.dir_train, default.HCompV_scp, file_type='fea')

# flat start
#if exist %dirModel0% rmdir /s /q %dirModel0%
#mkdir %dirModel0%
run([
    'HCompV', '-T', '1', 
    '-C', default.config_train,
    '-m', 
    '-v', '0.01',
    '-S', default.HCompV_scp,
    '-M', default.dir_model0, 
    os.path.join(default.dir_model, default.name_proto)
    ])
