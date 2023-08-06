'''新手的第一次尝试'''
import sys
def print_lol(the_list, indent = False, level = 0, fh = sys.stdout):
	'''head first python'''
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,indent,level+1, fh)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end='', file = fh)
			print(each_item, file = fh)
'''计时成绩的输入取名  Head First Python'''
def sanitize(time_string):
	if '-' in time_string:
		splitter = '-'
	elif ':' in time_string:
		splitter = ':'
	else:
		return(time_string)
	(mins, secs) = time_string.strip().split(splitter)
	return(mins + '.' + secs)
class Athlete:
	def  __init__(self, a_name, a_dob, a_times):
		self.name = a_name
		self.dob = a_dob
		self = a_times
	def top3(self):
		return(sorted(set([sanitize(t) for t in self]))[0:3])
class AthleteList(list):
	def __init__(self, a_name, a_dob = None, a_times = []):
		list.__init__([])
		self.name = a_name
		self.dob = a_dob
		self.extend(a_times)
	def top3(self):
		return(sorted(set([sanitize(t) for t in self]))[0:3])
def get_coach_data(filename):
	try:
		with open(filename) as f:
			data = f.readline()
		templ = data.strip().split(',')
		return(AthleteList(templ.pop(0), templ.pop(0), templ))
	except IOError as ioerr:
		print('File error: ' + str(ioerr))
		return(None)