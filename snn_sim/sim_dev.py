import sys
from snn_components import *

infile = sys.argv[1]
print(infile)

# if network == 1:
#     textfile = open("../smallnetdesc.txt", "r")
# else:
#     textfile = open("../shape_recog_net.txt", "r")



# Read the input file into a list of lines
with open(infile, 'r') as f:
    lines = f.readlines()


neuron_dict = {}
synapse_list = []

for line in lines:
    line = line.replace('\n', '')
    line = line.split(' ')
    # print(line)
    
    # Read in a neuron and create it, add it to neuron dictionary
    if line[0] == 'N':
        name = line[1]
        Vmem = Vrst
        fire = 0
        threshold = float(line[2])
        refractory = int(line[3])
        neuron_dict[name] = Neuron(0,0,threshold, refractory, name)
    
    # Read in a synapse and create it
    elif line[0] == 'S':
        pre = neuron_dict[line[1]]
        post = neuron_dict[line[2]]
        # print('Pre-neuron:', pre.Name, '  Thresh:', pre.vth)
        # print('Post-neuron:', post.Name, '  Thresh:', post.vth)

        Geff = float(line[3])
        delay = int(line[4])
        wp = float(line[5])*1e3 # TODO --> Right place to do this conversion???
        wn = float(line[6])*1e3
        syn = Synapse(wp, wn, delay, pre, post)
        synapse_list.append(syn)

    # A hacky way to stop reading network components  <-- TODO --> FIX THIS
    elif line[0] == '#':
        print('Finished reading network')
        break

    # Default case to catch all other lines
    else:
        pass

