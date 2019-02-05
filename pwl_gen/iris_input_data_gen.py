import sys
import numpy as np


if __name__ == '__main__':

	# Check to make sure the correct number of command line arguments is given
	if (len(sys.argv) == 6):
		infile = str(sys.argv[1])
		outfile = str(sys.argv[2])
		num_bins = int(sys.argv[3])
		cycle_gap = int(sys.argv[4])
		pin_names_file = str(sys.argv[5])
	else:
		print('Usage: python <iris_input.py> <input_file> <output_file> <num_bins> <cycle_gap>')
		exit(1)

	# print(infile)
	# print(num_bins)
	# print(cycle_gap)

	# Get all of the input pin names from the input file
	pin_names = []
	with open(pin_names_file, 'r') as pnf:
		lines = pnf.readlines()
		for line in lines:
			pin_names.append(line.rstrip())

	# Read the data and labels from an input file
	data_in = np.genfromtxt(infile, dtype='float', usecols=range(4))
	labels_in = np.genfromtxt(infile, dtype='str', usecols=(4))

	# Combine the data and labels, shuffle the data, and split it back up
	temp_data = []
	labels = []
	comb = np.array([(data_in[i], labels_in[i]) for i in range(len(data_in))])
	np.random.shuffle(comb)
	for i in range(len(comb)):
		temp_data.append(comb[i][0])
		labels.append(comb[i][1])
	data = np.array(temp_data)




	# Print the shuffled data for a sanity check
	# for i in range(len(data)):
	# 	print(data[i], ' : ', labels[i])


	# Get the shape of the data and create array of input values
	rows, cols = np.shape(data)
	inputs = np.zeros((rows, cols*num_bins))

	# Find the max and min for each column to determine bin sizes
	bin_sizes = []
	bin_cutoffs = []
	for c in range(cols):
		max_val = max(data[:,c])
		min_val = min(data[:,c])
		delta = round((max_val - min_val) / num_bins, 4)
		bin_sizes.append(delta)
		
		temp = []
		cutoff = min_val
		for n in range(num_bins):
			cutoff = cutoff + delta
			temp.append(round(cutoff,4))
		bin_cutoffs.append(temp)

	# A loop to bin all of the inputs
	for r in range(rows):
		for c in range(cols):
			for b in range(len(bin_cutoffs[c])):

				# The data point falls within the bin
				if (data[r][c] < bin_cutoffs[c][b]):
					inputs[r][c*num_bins+b] = 1
					break

				# The data point is the max value
				elif (b == len(bin_cutoffs[c])-1):
					inputs[r][c*num_bins+b] = 1

	# print(bin_cutoffs[0])
	# print(bin_sizes)
	# print(data[18])
	# print(inputs[18])

	# for r in range(rows):
	# 	print(r, ':', inputs[r])


	# Print the shuffled data to an output file with labels
	labels_out = 'labels_out.txt'
	with open(labels_out, 'w') as of:
		for r in range(len(labels)):
			of.write('{0} --> {1} --> {2}\n'.format(data[r], inputs[r], labels[r]))


	# Insert <cycle_gap> empty rows into the inputs array between each of the columns
	fires = np.zeros((rows*cycle_gap, cols*num_bins))
	for r in range(rows):
		fires[r*cycle_gap,:] = inputs[r,:]
	np.set_printoptions(threshold=np.nan)
	fires_transpose = np.transpose(fires)



	# Generate a stimulus file for Cadence simulation
	with open(outfile,'w') as of:

		# TODO
		# Add check to prevent moving to VSS between high cycles
		for r in range(len(fires_transpose)):

			of.write('_v{0} ({0} 0) vsource wave=\\[ 0 vss'.format(pin_names[r]))

			b = fires_transpose[r]
			for cycle in range(len(b)):
				of.write(' (tdel+{0}*tper) vss '.format(cycle+1))
				if (b[cycle] == 0):
					of.write('(tdel+{0}*tper+tf) vss '.format(cycle+1))
					of.write('(tdel+{0}*tper+twid-tf) vss '.format(cycle+1))
				else:
					of.write('(tdel+{0}*tper+tf) vdd '.format(cycle+1))
					of.write('(tdel+{0}*tper+twid-tf) vdd '.format(cycle+1))
				of.write('(tdel+{0}*tper+twid) vss'.format(cycle+1))

			of.write(' \\] type=pwl\n')




