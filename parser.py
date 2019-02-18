import csv
import numpy as np


class DataParser(object):

	def __init__(self, datafile):

		def readLinesFromCSVFile(infile):
			"""
			read each row from infile (str)
			"""
			rows = []
			with open(infile, 'r') as csvf:
				reader = csv.reader(csvf)
				for row in reader:
					rows.append(row)
			csvf.close()
			return rows


		# True if leap year, False if common year
		leap_year = lambda yr: (yr%400==0) or (yr%4==0 and not (yr%100==0))

		def yepo(date):
			day, month, year = np.array(date.split('/')).astype(int)

			# --- define an array of days per month in a common year
			monub = np.hstack((0, np.tile(np.hstack((31, np.tile((30, 31), 3))), 2)[:-2]))
			# --- check if leap year
			monub[2] = 28+int(leap_year(year))

			yrnub = np.hstack((0, 365+np.array(list(map(leap_year, 2000+np.arange(20)))).astype(int)))

			return yrnub.cumsum()[year-2000] + monub.cumsum()[month-1] + day - 1 


		def epoch(date, clock):
			hour, minute, second = np.array(clock.split(':')).astype(int)
			return (((yepo(date)*24 + hour)*60)+minute)*60+second


		data = readLinesFromCSVFile(infile=datafile)
		self.hdr  = data[0]
		del data[0]
		data = np.array([x[0].split(';') for x in data])

		self.date = np.array([x[0] for x in data])
		self.time = np.array([x[1] for x in data])
		self.epo = np.array([epoch(x[0], x[1]) for x in data])
		self.apwr = np.array([float(x[2]) if '?' not in x[2] else -1 for x in data])
		self.rpwr = np.array([float(x[3]) if '?' not in x[2] else -1 for x in data])
		self.volt = np.array([float(x[4]) if '?' not in x[2] else -1 for x in data])
		self.itns = np.array([float(x[5]) if '?' not in x[2] else -1 for x in data])
		self.sm1 = np.array([float(x[6]) if '?' not in x[2] else -1 for x in data])
		self.sm2 = np.array([float(x[7]) if '?' not in x[2] else -1 for x in data])
		self.sm3 = np.array([float(x[8]) if '?' not in x[2] else -1 for x in data])

		return
