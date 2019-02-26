from subprocess import Popen, PIPE


def run_command(command):
	"""this function throws an exception if the return code is non-zero. 
	
	Note: 
		This code is copied from forced_alignment module and editted.
		https://git.webhosting.rug.nl/p253591/forced-alignment
	"""
	p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate(b"")
	if p.returncode != 0:
		raise Exception("Command failed: {}\n\nOutput:\n======={}\n\nError:\n======\n{}\n".format(
			' '.join(command), output.decode('utf-8'), err.decode('utf-8'))
		)
	return command, output.decode('utf-8'), err.decode('utf-8')


#def run_command_with_output(command):
#	p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
#	output, err = p.communicate(b"")
#	return output.decode()