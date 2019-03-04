import os

config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config_default')
config_hcopy = os.path.join(config_dir, 'config.HCopy')
config_train = os.path.join(config_dir, 'config.train')
config_rec   = os.path.join(config_dir, 'config.rec')
global_ded   = os.path.join(config_dir, 'global.ded')
mkphones_led = os.path.join(config_dir, 'mkphones.led')
sil_hed		 = os.path.join(config_dir, 'sil.hed')
