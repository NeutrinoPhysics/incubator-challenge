# /!\ requires the data file in the current directory

import os
import parser
import utils
import numpy as np


def foldMonth(mid):
	return np.where(datarr[:,1]==monlst[mid])[0]

def foldDay(mid):
	return np.where(datarr[:,0]==daylst[mid])[0]

def foldHour(mid):
	return np.where(timarr[:,0]==hrlst[mid])[0]

def AvgMonth(mid):
	 return data[:,fm[mid]].mean(axis=1)


def pc_proj(k):
	"""
	get the eigenvalues of principal component k
	"""
	return np.dot(data, pc[k].T) / (np.sqrt(np.sum(data**2, axis=1)) * np.sqrt(np.sum(pc[k]**2)))




if __name__ == '__main__':

	dfile = 'household_power_consumption.txt'
	elec = parser.DataParser(datafile=os.path.join(os.getcwd(), dfile))

	val = np.where((elec.apwr>=0)*(elec.rpwr>=0)*(elec.volt>=0)*(elec.itns>=0)*(elec.sm1>=0)*(elec.sm2>=0)*(elec.sm2>=0))[0]
	epoch = elec.epo[val]
	data = np.vstack((	elec.apwr[val],
					elec.rpwr[val],
					elec.volt[val],
					elec.itns[val],
					elec.sm1[val],
					elec.sm2[val],
					elec.sm3[val]
					))

	# --- standardize data to mean 0 and std 1
	data = utils.standardize(data=data)

	# --- PCA decomposition
	pc, var = utils.decompose(data=data, co=7)

	# --- eigenvalues
	coef = np.array(list(map(pc_proj, np.arange(co))))

	# --- reconstructed data from PCs
	rlc = np.dot(coef.T, pc)

	# --- residuals
	res = data - rlc
	sres = utils.smooth(curv=res, fs=100)


	# --- fetch date and time info
	date = elec.date[val]
	time = elec.time[val]

	datarr = np.array(list(map(utils.dateParser, date)))
	timarr = np.array(list(map(utils.timeParser, time)))

	monlst = np.sort(np.unique(datarr[:,1]))
	daylst = np.sort(np.unique(datarr[:,0]))
	hrlst = np.sort(np.unique(timarr[:,0]))


	# --- fold over months, days and hours
	fm = list(map(foldMonth, np.arange(12)))
	fd = list(map(foldDay, np.arange(31)))
	fh = list(map(foldHour, np.arange(24)))

	avmon = np.array(list(map(AvgMonth, np.arange(12))))

