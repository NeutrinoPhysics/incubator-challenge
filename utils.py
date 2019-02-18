import numpy as np
from sklearn.decomposition import PCA


def standardize(data):
	arr = data.copy()
	arr -= arr.mean(axis=1, keepdims=True)
	arr /= arr.std(axis=1, keepdims=True)
	return arr


def pc_proj(data, pc, k):
	"""
	get the eigenvalues of principal component k
	"""
	return np.dot(data, pc[k].T) / (np.sqrt(np.sum(data**2, axis=1)) * np.sqrt(np.sum(pc[k]**2)))


def smooth(curv, fs=25):
	"""
	smooth curve by high pass filtering in Fourier space
	frequencies above the 'fs'-th are removed
	"""

	rft = np.fft.rfft(curv)
	rft[:,fs:]=0.

	return np.fft.irfft(rft)


def dateParser(dstr):
	"""
	parse date string into array
	"""
	dd, mm, yyyy = dstr.split('/')
	return np.array([dd, mm, yyyy]).astype(int)



def timeParser(dstr):
	"""
	parse clock time string into array
	"""
	hh, mm, ss = dstr.split(':')
	return np.array([hh, mm, ss]).astype(int)


def decompose(data, co=7):
	"""
	PCA decomposition of 'data' up to component 'co'
	"""
	mla = PCA(n_components=co)
	
	X = mla.fit_transform(data)
	mla.fit(data)
	
	# variance
	var = mla.explained_variance_ratio_
	
	# standardize principal components
	pc = mla.components_
	pc /= pc.std(axis=1, keepdims=True)

	return pc, var