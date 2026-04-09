import pickle

def main():
	ids = [1, 2, 3]

	bytes_ids = pickle.dumps(ids)

	return bytes_ids
