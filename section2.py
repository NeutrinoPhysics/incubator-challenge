import numpy as np

def road(N=10, M=5, T=20):
	"""
	N : number of positions
		int

	M : number of cars
		int

	T : number of total rounds
		int
	"""
	positions = np.arange(N)+1

	# --- inititation step
	occupied = np.zeros(N, dtype=bool)
	occupied[:M]=~occupied[:M]

	step = 0

	# --- loop
	while step < T:
		
		step+=1
		
		# --- determine which cars have a legal move
		whocanmove = np.where(np.hstack((np.diff(occupied), np.logical_xor(occupied[-1],occupied[0]))) * occupied)[0]
		
		# --- draw randomly from sample of cars that can legally move
		whomoves = np.random.choice(a=whocanmove, size=1)[0]
		
		# --- check if last cell
		final = whomoves+1 if whomoves < N-1 else 0
		
		# --- alter values in position array:
		#     car leaves currently occupied cell
		#     consecutive unoccupied cell becomes occupied
		occupied[final] = ~occupied[final]
		occupied[whomoves] = ~occupied[whomoves]

		#print('car in position [{}] moves to [{}]\n'.format(whomoves, final))

	# --- return array of occupied positions
	return positions[occupied]


def launch_road(simu=100, N=10, M=5, T=20):
	"""
	launch road simulation 'simu' amount of times
	for statistical convergence
	"""
	distrib = np.ndarray((simu,M), dtype=int)
	for k in range(simu):
		distrib[k,:] = road(N=N,M=M,T=T)

	# --- expected value of the average position
	E_A = np.mean(distrib, axis=1).mean()

	# --- expected value of the standard deviation on the position
	E_S = np.std(distrib, axis=1).mean()

	# --- standard deviation of the average position
	D_A = np.mean(distrib, axis=1).std()

	# --- standard deviation of the standard deviation on the position
	D_S = np.std(distrib, axis=1).std()

	print('--- {} iterances of N={}, M={} and T={} ---'.format(simu, N, M, T))
	print('expected value of A: {}'.format(np.round(E_A,10)))
	print('expected value of S: {}'.format(np.round(E_S,10)))
	print('standard deviation of A: {}'.format(np.round(D_A,10)))
	print('standard deviation of S: {}\n'.format(np.round(D_S,10)))


	return


if __name__== '__main__':

	# ---- how many times do we launch the simulation ?
	simu = 10000

	launch_road(simu=simu, N=10, M=5, T=20)
	launch_road(simu=simu, N=25, M=20, T=50)
