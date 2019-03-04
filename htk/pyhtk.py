"""
The module to use HTK (Hidden markov model Tool Kit).
"""
import sys
import os
os.chdir(r'C:\Users\Aki\source\repos\toolbox\htk')
#from subprocess import Popen, PIPE
import re
from tempfile import NamedTemporaryFile
import shutil
import glob

import pandas as pd

from . import defaultfiles as default
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import file_handling as fh
from scripts import run_command


class HTK:
	curr_dir = os.path.dirname(os.path.abspath(__file__))
	mkhmmdefs_pl = os.path.join(curr_dir, 'mkhmmdefs.pl')

	def __init__(self, 
			  config_dir,
			  phoneset,
			  lexicon_file,
			  feature_size,
			  feature_kind=None,
			  config_hcopy=default.config_hcopy,
			  config_train=default.config_train,
			  config_rec=default.config_rec,
			  global_ded=default.global_ded,
			  mkphones_led=default.mkphones_led,
			  sil_hed=default.sil_hed):
		
		# user define.
		self.lexicon_file = lexicon_file
		self.feature_size = feature_size

		# default settings.
		self.config_hcopy = config_hcopy
		self.config_train = config_train
		self.config_rec   = config_rec
		self.global_ded	  = global_ded
		self.mkphones_led = mkphones_led
		self.sil_hed	  = sil_hed 

		# set feature kind.
		# if not specified, load it from config.HCopy
		if feature_kind == None:
			with open(config_hcopy, 'r') as f:
				lines = f.read().replace('\t', '').split('\n')
			line = [line for line in lines if 'TARGETKIND' in line]
			line = line[0].replace(' ', '') # remove space
			line = line.split('#')[0]		# remove comments
			self.feature_kind = line.split('=')[1]
		else:
			self.feature_kind = feature_kind

		# files to be made.
		self.phonelist_txt = os.path.join(config_dir, 'phonelist.txt')
		self.phonelist_with_sp_txt = os.path.join(config_dir, 'phonelist_with_sp.txt')
		self.create_phonelist_file(phoneset, self.phonelist_txt)
		self.create_phonelist_file(phoneset, self.phonelist_with_sp_txt, with_sp=True)

		self.command = ''
		self.output = ''
		self.error  = ''

		return


	def _tokenize(self, text):
		""" extract only text as a list format. symbols, numbers and '_' are removed.
		"""
		return re.findall(r'[^\W\d_]+', text)


	def can_be_ascii(self, sentence):
		"""check if the sentence can be written in ascii. if not, return -1.
		"""
		try:
			sentence_bytes = bytes(sentence, 'ascii')
			return 0
		except UnicodeEncodeError:
			return -1

		return


	def create_phonelist_file(self, phoneset, phonelist_txt, with_sp=False):
		with open(phonelist_txt, 'wb') as f:
			phonelist_string = '\n'.join(phoneset) + '\nsil\n'
			if with_sp:
				phonelist_string = phonelist_string + 'sp\n'
			f.write(bytes(phonelist_string, 'ascii'))
		return


	def create_label_file(self, sentence, label_file):
		"""Save an orthographycal transcription (or sentence) to the HTK label file.
	
		Args: 
			sentence (str): sentence to store in the label_file.
			label_file (path): path to the text file in which each word is written on a line in upper case.

		"""
		#with open(label_file, 'w', encoding="utf-8") as f:
		#	f.write()
		with open(label_file, 'wb') as f:
			label_string = '\n'.join(self._tokenize(sentence.upper())) + '\n'
			f.write(bytes(label_string, 'ascii'))
		return


	def label2mlf(self, label_dir, mlf_file):
		"""Combine all label files (*.lab) in the directory as a master label file (.mlf)."""
		lab_list = glob.glob(os.path.join(label_dir, '*.lab'))
		with open(mlf_file, 'wb') as fmlf:
			fmlf.write(bytes('#!MLF!#\n', 'ascii'))
			for lab_file in lab_list:
				filename = os.path.basename(lab_file)
				fmlf.write(bytes('\"*/{}\"\n'.format(filename), 'ascii'))
				with open(lab_file) as flab:
					lines = flab.read()
				fmlf.write(bytes(lines + '.\n', 'ascii'))
		return


	def mlf_word2phone(self, mlf_phone, mlf_word):
		self.command, self.output, self.error = run_command([
			'HLEd', '-l', '*', 
			'-d', self.lexicon_file,
			'-i', mlf_phone, 
			self.mkphones_led,
			mlf_word
		])


	def create_dictionary(self, sentence, log_txt, dictionary_file):
		""" when the length of the filename exceeds 32 characters, error.
		"""
		label_file = NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
		label_file.close()
		self.create_label_file(sentence, label_file.name)

		phonelist_txt = NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
		phonelist_txt.close()
	
		self.command, self.output, self.error = run_command([
			'HDMan', '-w', label_file.name,
			'-g', self.global_ded,
			'-n', phonelist_txt.name,
			'-l', log_txt, 
			dictionary_file, 
			self.lexicon_file
		])

		os.remove(label_file.name)
		os.remove(phonelist_txt.name)

		return


	def read_number_of_missing_words(self, log_txt):
		with open(log_txt, encoding='utf-8') as f:
			lines = f.read()
		result_ = re.findall(r'[\d]+ words required, [\d]+ missing', lines)
		if len(result_) == 1:
			result = result_[0].split(' ')
		elif len(result_) == 0:
			print('{} has no line of missing word information.'.format(log_txt))
			raise
		else:
			print('{} includes multiple lines of missing word information.'.format(log_txt))
			raise
		return int(result[3])


	def get_number_of_missing_words(self, sentence, dictionary_file, lexicon_file):
		log_txt = NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
		log_txt.close()
		self.create_dictionary(
			sentence, log_txt.name, dictionary_file)
		number_of_missing_words = self.read_number_of_missing_words(log_txt.name)
		os.remove(log_txt.name)
		return number_of_missing_words


	def wav2mfc(self, hcopy_scp):
		self.command, self.output, self.error = run_command([
			'HCopy','-C', self.config_hcopy,
			'-S', hcopy_scp
		])
		return


	def _create_proto(self, proto):
		"""proto: a text file which includes the initial model. 
		"""
		feature_size = self.feature_size
		if feature_size % 10 == 0:
			lines_mean = ('0.0 ' * 10 + '\n') * (feature_size // 10)
			lines_variance = ('1.0 ' * 10 + '\n') * (feature_size // 10)
		else:
			lines_mean = ('0.0 ' * 10 + '\n') * (feature_size // 10) + ('0.0 ' * (feature_size % 10) + '\n')
			lines_variance = ('1.0 ' * 10 + '\n') * (feature_size // 10) + ('1.0 ' * (feature_size % 10) + '\n')

		feature_size_str = str(feature_size)
		with open(proto, 'wb') as f:
			line = '~o <VecSize> ' + feature_size_str + ' <' + self.feature_kind + '><DiagC> <StreamInfo> 1 ' + feature_size_str + '\n'
			f.write(bytes(line, 'ascii'))
			f.write(bytes('<BeginHMM>\n', 'ascii'))
			f.write(bytes('<NUMSTATES> 5\n', 'ascii'))
		
			for states in ['2', '3', '4']:
				f.write(bytes('<STATE> ' + states + '<NUMMIXES> 1\n', 'ascii'))
				f.write(bytes('<SWeights> 1 1\n', 'ascii'))		
				f.write(bytes('<STREAM> 1\n', 'ascii'))
				f.write(bytes('<MIXTURE> 1 1.000000e+00\n', 'ascii'))

				f.write(bytes('<MEAN> ' + feature_size_str + '\n', 'ascii'))
				f.write(bytes(lines_mean, 'ascii'))

				f.write(bytes('<VARIANCE> ' + feature_size_str + '\n', 'ascii'))
				f.write(bytes(lines_variance, 'ascii'))

			f.write(bytes('<TRANSP> 5\n', 'ascii'))	
			f.write(bytes('0.000000e+00 1.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00\n', 'ascii')) 
			f.write(bytes('0.000000e+00 6.000000e-01 4.000000e-01 0.000000e+00 0.000000e+00\n', 'ascii')) 
			f.write(bytes('0.000000e+00 0.000000e+00 6.000000e-01 4.000000e-01 0.000000e+00\n', 'ascii')) 
			f.write(bytes('0.000000e+00 0.000000e+00 0.000000e+00 6.000000e-01 4.000000e-01\n', 'ascii')) 
			f.write(bytes('0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00\n', 'ascii')) 
			f.write(bytes('<ENDHMM>\n', 'ascii'))

		return


	def flat_start(self, HCompV_scp, model_dir):
		"""
		Args:
			config_train:
			HCompV_scp: a script file.
			model_dir: the directory.
		"""
		proto = r'c:\OneDrive\Research\rug\experiments\acoustic_model\fame\htk\config\proto'
		self._create_proto(proto)

		self.command, self.output, self.error = run_command([
			'HCompV', '-T', '1', 
			'-C', self.config_train,
			'-f', '0.01',
			'-m', 
			'-S', HCompV_scp,
			'-M', model_dir,
			proto
		])
		return


	def create_hmmdefs(self, proto, hmmdefs):
		""" allocate mean & variance to all phases in the phaselist """
	
		_, output, _ = run_command([
			'perl', 
			HTK.mkhmmdefs_pl,
			proto, 
			self.phonelist_txt
		])

		if os.name == 'nt':
			output = output.replace('\r', '')
			output = output.replace('\n', '\r\n')

		with open(hmmdefs, 'wb') as f:
			f.write(bytes(output, 'ascii'))

		return


	def create_macros(self, vFloors):
		macros = vFloors.replace('vFloors', 'macros')
		with open(vFloors, 'r') as f:
			lines = f.read()
		with open(macros, 'wb') as f:
			line = '~o <' + self.feature_kind + '> <VecSize> ' + str(self.feature_size)
			f.write(bytes(line + '\n' + lines, 'ascii'))
		return


	def re_estimation(self, hmmdefs, output_dir, HCompV_scp, mlf_file=None, macros=None):
		command_list = []
		command_list.extend([
			'HERest', '-T', '1', 
			'-C', self.config_train,
			'-v', '0.01', 
			'-t', '250.0', '150.0', '1000.0',
			'-H', hmmdefs, 
			'-M', output_dir
			])
		if not mlf_file==None:
			command_list.extend(
				['-I', mlf_file]
			)
		if not macros==None:
			command_list.extend(
				['-H', macros]
			)
		command_list.extend(
			['-S', HCompV_scp, self.phonelist_txt]
		)

		self.command, self.output, self.error = run_command(command_list)
		
		return


	def _network2lattice(self, network_file, lattice_file):
		"""creats word level lattice files from a text file syntax description containing a set of rewrite rules based on extended Backus-Naur Form (EBNF).

		Args:
			network_file: word network.
			lattice_file: word level lattice file.

		Reference:
			http://www1.icsi.berkeley.edu/Speech/docs/HTKBook/node247.html

		"""
		self.command, self.output, self.error = run_command([
			'HParse', network_file, lattice_file
		])
		return


	def recognition(self, lattice_file, hmmdefs, HVite_scp, lexicon_file=None):
		if lexicon_file==None:
			lexicon_file = self.lexicon_file

		self.command, self.output, self.error = run_command([
			'HVite', '-T', '1', 
			'-C', self.config_rec, 
			'-w', lattice_file, 
			'-H', hmmdefs, 
			lexicon_file, 
			self.phonelist_txt, 
			'-S', HVite_scp
		])
		return self._load_recognition_result()


	def _load_recognition_result(self):
		""" still under testing ... 

		Args:
			output: output obtained by recognition().

		"""
		output = self.output.split('\r\n')

		# format the output.
		output_ = ' '.join(output).split('File: ')
		results = pd.DataFrame(index=[], columns=['filename', 'sequence', 'likelihood'])
		for line in output_:
			# sample of a line: 
			# File: xxxxxx.fea it ii it it it  ==  [368 frames] -111.7648 [Ac=-41129.5 LM=0.0] (Act=11.0)
			filename = line.split(' ')[0]
			sequence = ' '.join(line.split(' ')[1:]).split(' == ')[0].strip()
			line_ = line.replace(filename, '').replace(sequence, '')
			likelihood = re.findall(r'[-\d.]+', line_)[1]
	
			result_ = pd.Series([filename, sequence, likelihood], index=results.columns)
			results = results.append(result_, ignore_index = True)
			#print('{0}: {1} ({2})'.format(filename, sequence, likelihood))

		return results


	def calc_recognition_performance(self, HResults_scp, lexicon_file=None):
		if lexicon_file==None:
			lexicon_file = self.lexicon_file

		self.command, self.output, self.error = run_command([
			'HResults', '-T', '1', 
			lexicon_file, 
			'-S', HResults_scp
		])
		return self._load_recognition_performance()


	def _load_recognition_performance(self):
		output_ = self.output.split('------------------------ Overall Results --------------------------\r\n')[1]
		per_sentence_ = output_.split('\r\n')[0]
		performance = re.findall(r'[\d.]+', per_sentence_)
		per_sentence = dict()
		per_sentence['accuracy'] = float(performance[0])
		per_sentence['correct']  = int(performance[1])
		per_sentence['substitution'] = int(performance[2])
		per_sentence['total']	 = int(performance[3])

		per_word_	  = output_.split('\r\n')[1]
		performance = re.findall(r'[\d.]+', per_word_)
		per_word = dict()
		per_word['accuracy']	 = float(performance[0])
		per_word['correct']		 = int(performance[2])
		per_word['deletion']	 = int(performance[3])
		per_word['substitution'] = int(performance[4])
		per_word['insertion']    = int(performance[5])
		per_word['total']		 = int(performance[6])

		return per_sentence, per_word


	def get_recognition_accuracy(self, 
							  test_dir, file_type, 
							  lattice_file, hmmdefs, lexicon_file=None):
		if lexicon_file==None:
			lexicon_file = self.lexicon_file

		# recognition
		HVite_scp = NamedTemporaryFile(mode='w', delete=False)
		HVite_scp.close()
		fh.make_filelist(test_dir, HVite_scp.name, file_type=file_type)
		output = self.recognition(
			lattice_file, 
			hmmdefs, 
			HVite_scp.name, 
			lexicon_file=lexicon_file)
		os.remove(HVite_scp.name)

		# calculate the performance
		HResult_scp = NamedTemporaryFile(mode='w', delete=False)
		HResult_scp.close()
		fh.make_filelist(test_dir, HResult_scp.name, file_type='rec')	
		performance = self.calc_recognition_performance(
			HResult_scp.name, 
			lexicon_file=lexicon_file)

		return performance


	def re_estimation_until_saturated(
		self, output_dir, model0_dir, improvement_threshold, hcompv_scp, 
		test_dir, file_type, lattice_file, mlf_file=None, lexicon_file=None):

		if lexicon_file==None:
			lexicon_file = self.lexicon_file
		if not os.path.exists(os.path.join(output_dir, 'iter0')):
			shutil.copytree(model0_dir, os.path.join(output_dir, 'iter0'))

		niter = 1
		accuracy_ = 0
		improvement = 100
		while improvement > improvement_threshold:
			hmm_n = 'iter' + str(niter)
			hmm_n_pre = 'iter' + str(niter-1)
			modeln_dir	   = os.path.join(output_dir, hmm_n)
			modeln_dir_pre = os.path.join(output_dir, hmm_n_pre) 
		
			# re-estimation
			fh.make_new_directory(modeln_dir, 'leave')
			self.re_estimation(
				os.path.join(modeln_dir_pre, 'hmmdefs'), 
				modeln_dir,
				hcompv_scp,
				mlf_file=mlf_file, 
				macros=os.path.join(modeln_dir_pre, 'macros'))

			# recognition
			per_sentence, per_word = self.get_recognition_accuracy( 
				test_dir, file_type, lattice_file, 
				os.path.join(modeln_dir, 'hmmdefs'), 
				lexicon_file=lexicon_file)
			accuracy = per_sentence['accuracy']
			improvement = accuracy - accuracy_
			print('accuracy of {0}: {1}[%] (improved {2:.2}[%])'.format(
				hmm_n, accuracy, improvement))
			accuracy_ = accuracy

			niter = niter + 1
		return niter - 1


	def _add_sp_to_hmmdefs(self, hmmdefs_pre, hmmdefs):
		with open(hmmdefs, 'wb') as fout:
			with open(hmmdefs_pre) as fin:
				lines = fin.read()
			fout.write(bytes(lines, 'ascii'))
			fout.write(bytes('~h "sp"\n', 'ascii'))
			fout.write(bytes('<BEGINHMM>\n', 'ascii'))
			fout.write(bytes('<NUMSTATES> 3\n', 'ascii'))
			fout.write(bytes('<STATE> 2\n', 'ascii'))
		
			lines = lines.split('\n')
			sil_state = lines[lines.index('~h "sil"'):]
		
			# mean, variance and gconst of 'sil'
			sil_state3_index = sil_state.index('<STATE> 3')
			sil_state4_index = sil_state.index('<STATE> 4')
			sil_state3 = sil_state[sil_state3_index+3:sil_state4_index]
			fout.write(bytes('\n'.join(sil_state3) + '\n', 'ascii'))
			fout.write(bytes('<TRANSP> 3\n', 'ascii'))

			# transp
			sil_transp = sil_state[sil_state.index('<TRANSP> 5')+3]
			sil_transp = sil_transp.strip().split(' ')
			fout.write(bytes('0.000000e+00 1.000000e+00 0.000000e+00\n', 'ascii'))
			fout.write(bytes('0.000000e+00 ' + sil_transp[2] + ' ' + sil_transp[3] + '\n', 'ascii'))
			fout.write(bytes('0.000000e+00 0.000000e+00 0.000000e+00\n', 'ascii'))
			fout.write(bytes('<ENDHMM>\n', 'ascii'))
		return


	def _tie_sp_to_sil(self, macros, hmmdefs, output_dir):
		self.command, self.output, self.error = run_command([
			'HHEd', 
			'-H', macros, 
			'-H', hmmdefs,
			'-M', output_dir,
			self.sil_hed, 
			self.phonelist_txt
		])
		return


	def add_sp(self, model_dir_pre, model_dir):
		hmmdefs_ = NamedTemporaryFile(mode='w', delete=False)
		hmmdefs_.close()

		# add sp to hmmdefs.
		self._add_sp_to_hmmdefs(
			os.path.join(model_dir_pre, 'hmmdefs'), 
			hmmdefs_.name)
		
		# update hmmdefs and macros.
		fh.make_new_directory(model_dir)
		self._tie_sp_to_sil(
			os.path.join(model_dir_pre, 'macros'), 
			hmmdefs_.name, 
			model_dir)

		os.rename(
			os.path.join(model_dir, os.path.basename(hmmdefs_.name)), 
			os.path.join(model_dir, 'hmmdefs'))
		os.remove(hmmdefs_.name)
		return


def increase_mixture(hmmdefs, nmix, output_dir, phonelist_txt):
	fh.make_new_directory(output_dir)
	header_file = os.path.join(output_dir, 'mix' + str(nmix) + '.hed')
	with open(header_file, 'wb') as f:
		f.write(bytes('MU ' + str(nmix) + ' {*.state[2-4].mix}', 'ascii'))

	run_command([
		'HHEd', '-T', '1', 
		'-H', hmmdefs, 
		'-M', output_dir,
		header_file, phonelist_txt
	])








#if __name__ == '__main__':
	
#def txt2label(file_txt, label_file):
#	"""
#	Convert an orthographycal transcription to the HTK label.  
#	:param path file_txt: path to the text file in which the orthographycal transcription of the utterance is written in one line.
#	:param path label_file: path to the text file in which the contents of file_txt is written as a word per line. 
#	"""
#	# read the first line where the sentence is written.
#	with open(file_txt, 'r') as f:
#		line1 = f.readline()

#	# remove space at the end and comma
#	line1 = line1.rstrip()
#	line1 = line1.replace(',', '')

#	# write each word in a capital letter 
#	line1list = line1.split(' ')
#	with open(label_file, 'w') as f:
#		for word in line1list:
#			f.write("%s\n" % word.upper())


#def lab2HTKdic(label_file, fileHTKdic, lex, connect):
#	"""
#	Make a HTK dictionary file from a HTK label file.
#	Each word in the label file is first searched in database. 
#	If not found, the Grapheme-to-Phone(G2P) program is used.
#	:param path label_file: path to the text file in which the contents of file_txt is written as a word per line. 
#	:param path fileHTKdic: path to the output dictionary file in which pronunciation variants will be written. 
#	:param instance lex: an instance of class cLexicon.
#	:param pypyodbc connect: an object of pypyodbc.
#	"""
#	cursor  = connect.cursor()
#	tableList  = ['2010_2510_lexicon_pronvars_HTK', 'lexicon_pronvars_g2p', 'lexicon_pronvars_ipa']

#	with open(label_file, 'r') as f:
#		lines = f.read()
#		words = lines.split()

#	with open(fileHTKdic, 'w') as f:
#		for WORD in words:
#			word = WORD.lower()
#			rows = np.array([])
#			for tableNum in range(0, len(tableList)):
#				SQL_string = """SELECT word, pronunciation FROM %s WHERE word =?""" %(tableList[tableNum]) 
#				cursor.execute(SQL_string, (word,))
#				rows_ = cursor.fetchall()
#				rows = np.append(rows, rows_)
		
#			# if the pronunciations are found in the database, retreive them.
#			# otherwise obtain the pronunciation using g2p.
#			if len(rows) > 2:
#				# reshape into d x 2 array
#				htkdic_ = rows.reshape((-1, 2))
#				# remove duplicates
#				htkdic  = np.unique(htkdic_, axis=0)
#			else:
#				# get pronunciation using g2p
#				fileWordList = tempfile.NamedTemporaryFile(mode='w', delete=False)
#				fileWordList.write("%s\n" % (word))
#				fileWordList.close()
#				htkdic = lex.g2p2db(fileWordList.name, connect)
#				fileWordList.close()
#				os.remove(fileWordList.name)

#			# output htkdic
#			for line in htkdic:
#				word = line[0].upper()
#				pron = line[1]
#				f.write("{0}\t{1}\n".format(word, pron))


#def loadHTKdic(fileHTKdic):
#	"""
#	load dic file which is used for HTK.
#	:param path fileHTKdic: path to the output dictionary file in which pronunciation variants will be written. 
#	"""
#	HTKdic = []
	
#	with open(fileHTKdic, 'r') as f:
#		lines = f.read()
#		lines = lines.split('\n')

#		for line in lines:
#			line = line.split('\t')
#			if len(line) > 1:
#				HTKdic.append(line)
				
#	return np.array(HTKdic)


#def HTKdic2list(fileHTKdic):
#	"""
#	load an HTK dictionary file as a list.
#	:param path fileHTKdic: the path to an HTK dictionary file in which [word] /t [pronunciation] is written each line.
#	"""
#	with open(fileHTKdic, 'r') as fin:
#		lines_ = fin.read()
#		# split all text into lines
#		lines = lines_.split('\n')
	
#	htkdic = []	
#	for line in lines:
#		lineSplit = line.split('\t')
#		if len(lineSplit) == 2:
#			word		  = lineSplit[0].lower()
#			pronunciation = lineSplit[1]
#			htkdic.append([word, pronunciation])
#	return np.array(htkdic)


#def doHVite(fileWav, label_file, fileHTKdic, fileFA, configHVite, filePhoneList, AcousticModel):
#	"""
#	Forced alignment using HVite of HTK.
#	:param path fileWav: path to the wav file in which the utterance was recorded.
#	:param path label_file: path to the text file in which the contents of file_txt is written as a word per line. 
#	:param path fileHTKdic: path to the HTK dictionary file in which pronunciation variants are written.
#	:param path fileFA: path to the output file in which forced alignment (100ns unit) will be written.
#	:param path configHVite: path to the config file of HVite.
#	:param path filePhoneList: path to the list of phone used in the acoustic model and in the HTK dictionary file.
#	:param path AcousticModel: path to the acoustic model.
#	"""
#	with open(label_file, 'r') as f:
#		lines = f.read()

#	# Master Label File (= list of label files.)
#	fileMlf = tempfile.NamedTemporaryFile(mode='w', delete=False)
#	fileMlf.write("#!MLF!#\n")
#	fileMlf.write('"' + label_file + '"\n')
#	fileMlf.write(lines)
#	fileMlf.close()

#	# script
#	fileScp = tempfile.NamedTemporaryFile(mode='w', delete=False)
#	fileScp.write("%s" % (fileWav))
#	fileScp.close()

#	# HVite
#	subprocessStr = 'HVite -T 1 -a -C ' + configHVite + ' -H ' + AcousticModel + ' -m -I ' + fileMlf.name + ' -i ' + fileFA + ' -S ' + fileScp.name + ' ' + fileHTKdic + ' ' + filePhoneList
#	subprocess.call(subprocessStr, shell=True)

#	# termination process
#	os.remove(fileMlf.name)
#	os.remove(fileScp.name)


#def conv100ns2ms(fileFA_in_100ns, fileFA_in_ms):
#	"""
#	Convert the unit of forced alignment from 100ns to ms.
#	:param path fileFA_in_100ns: path to the forced alignment file written in the unit of 100ns.
#	:param path fileFA_in_ms: path to the output forced alignment file written in the unit of ms.  
#	"""
#	with open(fileFA_in_100ns, 'r') as fin:
#		with open(fileFA_in_ms, 'w') as fout:
#			line = fin.readline()
#			fout.write(line)
#			line = fin.readline()
#			fout.write(line)

#			while line:
#				line = fin.readline()
#				dur = line.split()

#				# Each line of forced alignment file is:
#				# [durStart] [durEnd] [phoneme] [likelihood] [word]
#				if len(dur) == 4 or len(dur) == 5:
#					# convert 100ns -> ms
#					dur[0] = float(dur[0])/10000
#					dur[1] = float(dur[1])/10000
#					if len(dur) == 4:
#						fout.write('{0} {1} {2} {3}\n'.format(dur[0], dur[1], dur[2], dur[3]))
#					elif len(dur) == 5:
#						fout.write('{0} {1} {2} {3} {4}\n'.format(dur[0], dur[1], dur[2], dur[3], dur[4]))
#				else:
#					fout.write(line)


#def ForcedAlignment(fileWav, file_txt, fileOut, configFile, saveIntermediateFiles):
#	"""
#	Forced Alignment
#	:param path fileWav: path to the wav file in which the utterance was recorded.
#	:param path file_txt: path to the text file in which the orthographycal transcription of the utterance is written in one line.
#	:param path fileOut: path to the output file in which forced alignment will be written in the unit of ms.
#	:param path configFile: path to the general config file (not the config file for HVite).
#	:param int saveIntermediateFile: if intermediate files (label file and dictionary file) should be saved. 0:no, 1:yes
#	"""
#	# label file: the list of words that appears in the wave file.
#	#	should be in the same folder where wav file is stored.
#	label_file = fileWav.replace('.wav', '.lab')
#	# dic file: the pronunciation dictionary in which pronunciation(s) of each word in the label file are described.
#	fileHTKdic = fileWav.replace('.wav', '.dic')
#	# forced alignment output
#	fileFA = tempfile.NamedTemporaryFile(delete=False)
#	fileFA.close()


#	# load the config file
#	config = configparser.ConfigParser()
#	config.sections()
#	config.read(configFile)

#	dbLexicon	  = config['cLexicon']['dbLexicon']
#	scriptBarbara = config['cLexicon']['scriptBarbara']
#	exeG2P		  = config['cLexicon']['exeG2P']

#	configHVite	  = config['pyHTK']['configHVite']
#	filePhoneList = config['pyHTK']['filePhoneList']
#	AcousticModel = config['pyHTK']['AcousticModel']


#	# make database connection
#	param = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};dbq=" + dbLexicon + ";"
#	connect = pypyodbc.connect(param)


#	# instance of class lexicon
#	if sys.platform == 'win32':
#		scriptBarbara = scriptBarbara.replace('\\\\', '\\')
#	lex = cLexicon.lexicon(scriptBarbara, exeG2P)


#	# load the orthographical transcription 
#	# and output that word by word (e.g. one word per line) in capital letters...
#	txt2label(file_txt, label_file)
	
#	# for each words in the label file pronunciation(s) are searched in lexicon database...
#	lab2HTKdic(label_file, fileHTKdic, lex, connect)

#	# forced alignment using HVite
#	doHVite(fileWav, label_file, fileHTKdic, fileFA.name, configHVite, filePhoneList, AcousticModel)
#	conv100ns2ms(fileFA.name, fileOut)


#	# termination process
#	if saveIntermediateFiles == 0:
#		os.remove(label_file)
#		os.remove(fileHTKdic)
#	os.remove(fileFA.name)
#	connect.close()