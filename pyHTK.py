"""
The module to use HTK (Hidden markov model Tool Kit).
"""
import sys
import os
os.chdir(r'C:\Users\A.Kunikoshi\source\repos\toolbox\toolbox')

from subprocess import Popen, PIPE

#import tempfile
#import subprocess
#import configparser

#import pypyodbc
#import numpy as np

#import cLexicon

def run(command):
    """this function throws an exception if the return code is non-zero, then all the files HVite used are printed to std for convenience.
    
    Note: 
        This code is copied from forced_alignment module.
        https://git.webhosting.rug.nl/p253591/forced-alignment
    """
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"")
    rc = p.returncode
    if rc != 0:
        raise Exception("Command failed: {}\n\nOutput:\n======={}\n\nError:\n======\n{}\n".format(
            ' '.join(command), output.decode('utf-8'), err.decode('utf-8'))
        )





#def txt2label(file_txt, file_lab):
#	"""
#	Convert an orthographycal transcription to the HTK label.  
#	:param path file_txt: path to the text file in which the orthographycal transcription of the utterance is written in one line.
#	:param path file_lab: path to the text file in which the contents of file_txt is written as a word per line. 
#	"""
#	# read the first line where the sentence is written.
#	with open(file_txt, 'r') as f:
#		line1 = f.readline()

#	# remove space at the end and comma
#	line1 = line1.rstrip()
#	line1 = line1.replace(',', '')

#	# write each word in a capital letter 
#	line1list = line1.split(' ')
#	with open(file_lab, 'w') as f:
#		for word in line1list:
#			f.write("%s\n" % word.upper())


#def lab2HTKdic(file_lab, fileHTKdic, lex, connect):
#	"""
#	Make a HTK dictionary file from a HTK label file.
#	Each word in the label file is first searched in database. 
#	If not found, the Grapheme-to-Phone(G2P) program is used.
#	:param path file_lab: path to the text file in which the contents of file_txt is written as a word per line. 
#	:param path fileHTKdic: path to the output dictionary file in which pronunciation variants will be written. 
#	:param instance lex: an instance of class cLexicon.
#	:param pypyodbc connect: an object of pypyodbc.
#	"""
#	cursor  = connect.cursor()
#	tableList  = ['2010_2510_lexicon_pronvars_HTK', 'lexicon_pronvars_g2p', 'lexicon_pronvars_ipa']

#	with open(file_lab, 'r') as f:
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


#def doHVite(fileWav, file_lab, fileHTKdic, fileFA, configHVite, filePhoneList, AcousticModel):
#	"""
#	Forced alignment using HVite of HTK.
#	:param path fileWav: path to the wav file in which the utterance was recorded.
#	:param path file_lab: path to the text file in which the contents of file_txt is written as a word per line. 
#	:param path fileHTKdic: path to the HTK dictionary file in which pronunciation variants are written.
#	:param path fileFA: path to the output file in which forced alignment (100ns unit) will be written.
#	:param path configHVite: path to the config file of HVite.
#	:param path filePhoneList: path to the list of phone used in the acoustic model and in the HTK dictionary file.
#	:param path AcousticModel: path to the acoustic model.
#	"""
#	with open(file_lab, 'r') as f:
#		lines = f.read()

#	# Master Label File (= list of label files.)
#	fileMlf = tempfile.NamedTemporaryFile(mode='w', delete=False)
#	fileMlf.write("#!MLF!#\n")
#	fileMlf.write('"' + file_lab + '"\n')
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
#	file_lab = fileWav.replace('.wav', '.lab')
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
#	txt2label(file_txt, file_lab)
	
#	# for each words in the label file pronunciation(s) are searched in lexicon database...
#	lab2HTKdic(file_lab, fileHTKdic, lex, connect)

#	# forced alignment using HVite
#	doHVite(fileWav, file_lab, fileHTKdic, fileFA.name, configHVite, filePhoneList, AcousticModel)
#	conv100ns2ms(fileFA.name, fileOut)


#	# termination process
#	if saveIntermediateFiles == 0:
#		os.remove(file_lab)
#		os.remove(fileHTKdic)
#	os.remove(fileFA.name)
#	connect.close()


