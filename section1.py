# /!\ have the .csv and .xls files in the current directory
# /!\ requires pyexcel_xls, install w/ 'pip install pyexcel-xls'

import os
import csv
import pyexcel_xls
import numpy as np

# === functions


# True if leap year, False if common year
leap_year = lambda yr: (yr%400==0) or (yr%4==0 and not (yr%100==0))


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


def incidentHisto():
	"""
	histogram of incidents
	"""
	histo = np.zeros(incidentKeys.size, dtype=int)
	for s in range(sz):
		histo+=(incidentFDNY[s] == incidentKeys).astype(int)
	return histo


def epoch(dstr):
	"""
	epoch in seconds from date and time string
	with epoch = 0 at 
	January 1st, 2000, 00h00m00s
	
	- assumes all times local and in same location
	- does not account for daylights savings
	- does not account for leap seconds

	dstr : str
		date and time string
		format 'mm/dd/yyyy hh:mm:ss AM'
	"""
	date, clock, sun = dstr.split(' ')
	month, day, year = np.array(date.split('/')).astype(int)
	hour, minute, second = np.array(clock.split(':')).astype(int)
	hour-=(12*int(hour==12))  # if 12 am or pm, substract 12 to get 0
	hour+=(12*int(sun=='PM')) # if pm, add 12 to get 24 h format

	# --- define an array of days per month in a common year
	monub = np.hstack((0, np.tile(np.hstack((31, np.tile((30, 31), 3))), 2)[:-2]))
	# --- check if leap year
	monub[2] = 28+int(leap_year(year))

	yrnub = np.hstack((0, 365+np.array(list(map(leap_year, 2000+np.arange(20)))).astype(int)))

	epoch = (((( yrnub.cumsum()[year-2000] + monub.cumsum()[month-1] + day - 1 ) * 24) + hour * 60)+minute)*60+second

	return epoch


def dispatchTime(inc):
	"""
	compute dispatch time for an incident
	inc : int
		incident number
	"""
	if len(FDNY[inc][dti])==0 or len(FDNY[inc][ati])==0:
		dispt = -99 # arbitrary flag value
	else:
		declared = epoch(dstr=FDNY[inc][dti])
		arrived  = epoch(dstr=FDNY[inc][ati])
		dispt = arrived - declared
	return dispt


def CountIncidentsPerZip(idx):
	"""
	count number of incidents per unique zip code
	"""
	global czip
	czip[uzip==zipcode[idx]]+=1
	return

def CountPopulationPerZip(idx):
	"""
	count population size per unique zip code
	"""
	global pzip
	val = np.where(US2010[:,0]==uzip[idx])[0]
	#print(val)
	if len(val) >= 1:
		pzip[idx]=US2010[val[0],1]
	else:
		pzip[idx]=-1
	return



if __name__ == '__main__':


	# === read data files

	dataFile = [f for f in os.listdir(os.getcwd()) if f.endswith('.csv')]
	metaFile = [f for f in os.listdir(os.getcwd()) if f.endswith('.xls')]

	# --- read meta data for FDNY file
	metaData = pyexcel_xls.get_data(metaFile[0])
	incidentKeys = np.array([ik[0] for ik in metaData['INCIDENT TYPE'][1:]])

	# --- read the fire department data
	FDNY = readLinesFromCSVFile(dataFile[0])
	hdr  = FDNY[0] # get header
	del FDNY[0]    # remove header from rest of data
	sz=len(FDNY)   # number of rows in data

	# --- read the census data
	US2010 = readLinesFromCSVFile(dataFile[1])
	hdr2010  = US2010[0] # get header
	del US2010[0]        # remove header from rest of data
	US2010 = np.array(US2010) # convert to numpy array since data is small




	# === define data cuts

	# --- incident type.
	iti = np.array(['INCIDENT_TYPE_DESC' in x for x in hdr]).astype(int).argmax()
	incidentFDNY = [dt[iti] for dt in FDNY]
	falsecall = [dt[iti]=='710 - Malicious, mischievous false call, other' for dt in FDNY]
	buildingfire = [dt[iti]=='111 - Building fire' for dt in FDNY]
	smokescare = [dt[iti]=='651 - Smoke scare, odor of smoke' for dt in FDNY]
	cookingfire = [dt[iti]=='113 - Cooking fire, confined to container' for dt in FDNY]


	# --- location borough.
	bdi = np.array(['BOROUGH_DESC' in x for x in hdr]).astype(int).argmax()
	statenisland = [dt[bdi]=='3 - Staten Island' for dt in FDNY]
	manhattan = [dt[bdi]=='1 - Manhattan' for dt in FDNY]

	# --- presence or not of CO detector
	coi = np.array(['CO_DETECTOR_PRESENT_DESC' in x for x in hdr]).astype(int).argmax()
	cop = [dt[coi]=='Yes' for dt in FDNY]
	coa = [dt[coi]=='No' for dt in FDNY]

	# --- on scene units.
	uni = np.array(['UNITS_ONSCENE' in x for x in hdr]).astype(int).argmax()
	unitsonscene = np.array([int(dt[uni]) if len(dt[uni])>0 else 0 for dt in FDNY])

	# --- incident timings.
	dti = np.array(['INCIDENT_DATE_TIME' in x for x in hdr]).astype(int).argmax()
	ati = np.array(['ARRIVAL_DATE_TIME' in x for x in hdr]).astype(int).argmax()


	# --- zip code.
	zipi = np.array(['ZIP_CODE' in x for x in hdr]).astype(int).argmax()
	zipcode = np.array([FDNY[x][zipi] for x in np.where(buildingfire)[0]])
	uzip = np.unique(zipcode)
	czip = np.zeros(uzip.size, dtype=int)
	pzip = np.zeros(uzip.size, dtype=int)




	# === Question 1
	histo = incidentHisto()
	print('most common FDNY responde: {}'.format(incidentKeys[histo.argmax()]))
	print('proportion of response: {}'.format(histo.max()/histo.sum()))



	# === Question 2
	print('avrg nb of units on scene ratio between building fires and smoke scares: {}'.format(\
	np.mean(unitsonscene[buildingfire]) / np.mean(unitsonscene[smokescare])))



	# === Question 3
	print('Staten Island vs Manhattan false call rate ratio: {}'.format(\
	sum(np.logical_and(statenisland,falsecall)) / sum(np.logical_and(manhattan,falsecall))))



	# === Question 4
	dispatch = np.array(list(map(dispatchTime, np.where(buildingfire)[0])))
	dispatch = dispatch[dispatch>=0] # get rid of flagged events
	print('Q3: {} min'.format(np.percentile(dispatch, 75)/60.))



	# === Question 5

	# --- time and am/pm of incidents
	hrs = np.array([int(x[dti].split(' ')[1].split(':')[0]) for x in FDNY])
	sun = np.array([x[dti].split(' ')[-1] for x in FDNY])

	# --- conform to 24h format
	hrs[hrs==12]-=12
	hrs[sun=='PM']+=12

	# --- bin all incidents and cooking fires into hourly histograms
	beans = np.unique(hrs)
	binedges = np.hstack((beans, beans[-1]+1))-0.5
	hrs_all = np.histogram(hrs, bins=binedges)[0]
	cookfires = np.where(np.array(cookingfire)==True)[0]
	hrs_cook = np.histogram(hrs[cookfires], bins=binedges)[0]

	# -- define cooking rate
	cookrate = hrs_cook/hrs_all
	cooktime = cookrate.argmax()
	print('people cook most likely at {}h, when {} of all incidents are cooking fires'.format(cooktime, cookrate[cooktime]))





	# === Question 6
	
	# --- count incidents per zip code
	list(map(CountIncidentsPerZip, np.arange(zipcode.size)))
	
	# --- count population per zip code
	list(map(CountPopulationPerZip, np.arange(uzip.size)))
	
	# --- only consider zip codes in US Census data
	uzip=uzip[pzip>=0]
	czip=czip[pzip>=0]
	pzip=pzip[pzip>=0]

	# --- Pearson Product Moment Correlation Coefficient
	x = pzip - pzip.mean() # reduced population variable
	y = czip - czip.mean() # reduced count variable
	ppmc = (x*y).sum()/np.sqrt((x**2).sum()*(y**2).sum())
	r2 = ppmc**2
	print('Population size and number of building fires have correlation coefficient (squared): R^2 = {}'.format(r2))



	# === Question 7

	# --- histogram bin size and edges definition
	binedges = np.arange(20, 80, 10)
	beans = binedges[:-1]+np.diff(binedges[:2])[0]/2.

	# --- CO detector present dispatch time
	copdt = np.array(list(map(dispatchTime, np.where(cop)[0])))
	copdt = (copdt[copdt>=0])/60. # get rid of flagged events
	copb = np.histogram(copdt, binedges)[0]

	# --- CO detector absent dispatch time
	coadt = np.array(list(map(dispatchTime, np.where(coa)[0])))
	coadt = (coadt[coadt>=0])/60. # get rid of flagged events
	coab = np.histogram(coadt, binedges)[0]

	# --- linear regression
	freq = coab / copb
	slope, intercept = np.polyfit(x=np.delete(beans,3), y=np.delete(freq,3), deg=1)
	print('ratio of events lasting 39 minutes: {}'.format(intercept+slope*39))



	# === Question 8

	# --- Null Hypothesis, H0: response time not influenced by presence of CO detector
	Nco = coadt.size+copdt.size # total sample size
	# expected frequency of response time > 60 min, absence of CO detector
	erta = (sum(coadt>=60.)+sum(copdt>=60.)) * coadt.size / Nco
	# expected frequency of response time > 60 min, presence of CO detector
	ertp = (sum(coadt>=60.)+sum(copdt>=60.)) * copdt.size / Nco
	# --- chi2 test
	chi2 = (sum(coadt>=60.)-erta)**2/erta + (sum(copdt>=60.)-ertp)**2/ertp
	print('X2 of population size vs number of incidents: {}'.format(chi2))



