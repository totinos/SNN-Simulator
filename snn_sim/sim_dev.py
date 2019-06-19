import sys
import collections
from snn_components import *

import matplotlib.pyplot as plt

network_file = sys.argv[1]
#print(network_file)

input_dir = sys.argv[2]


# rng = Std_RNG()
rng = Chaos_RNG("lookup_geo_5_4.tbl", 0.7, 0.6625)
# for i in range(100):
#     rng.step()
#     # print(rng.get_vout())
#     # if rng.get_num_out() != 7 and rng.get_num_out() != 1:
#     print(rng.get_num_out())
# exit()

class INP_PROC:

    def __init__(self):

        self.inp_num = 0


    def step(self):
        
        self.input_file = input_dir + "/shape_" + str(self.inp_num).zfill(3) + ".txt"
        #print(self.input_file)
        
        # Read the input file into a list of lines
        with open(self.input_file, 'r') as f:
            lines = f.readlines()

        self.input_neuron_list = []
        self.input_synapse_list = []

        # Create "input neurons/synapses" to carry input spikes into the network
        for line in lines:
            line = line.replace(' \n', '')
            line = line.replace('\n', '')
            line = line.split(' ')
            line = [int(i) for i in line]

            # Create an input neuron and synapse, the post-neuron of the synapse is as yet unknown
            input_neuron = InputNeuron(line, "INP")
            # input_synapse = InputSynapse(Mp_in, Mn_in, 0, input_neuron, None)
            input_synapse = Synapse(Mp_in, Mn_in, 0, input_neuron, None)
            self.input_neuron_list.append(input_neuron)
            self.input_synapse_list.append(input_synapse)

        self.SIM_CYCLES = len(line)
        #print(SIM_CYCLES)
        
        self.inp_num += 1


inp_class = INP_PROC()

num_correct = 0

# Get the labels so that you can compare for correctness
input_labels = input_dir + "/shape_labels.txt"
with open(input_labels, "r") as f:
    labels = f.readlines()
for i in range(len(labels)):
    labels[i] = labels[i].replace("\n", "")
#print(labels)

# Try network for all shapes
while inp_class.inp_num < len(labels):
    
    # Get the next input file
    inp_class.step()


    # Read the network file into a list of lines
    with open(network_file, 'r') as f:
        lines = f.readlines()
    # print(len(lines))
    # exit()

    neuron_dict = {}
    synapse_list = []
    #rng.step()

    # UNTIL I KNOW HOW THIS ACTUALLY WORKS
    count = 0

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
            # neuron_dict[name] = StochasticNeuron(name, Vmem, threshold, refractory)
            # neuron_dict[name] = Neuron(name, Vmem, threshold, refractory)
            # neuron_dict[name] = Neuron(name, Vmem, threshold, refractory, stochastic=True, rng=rng)
            neuron_dict[name] = Neuron(name, Vmem, threshold, refractory, stochastic=False, rng=rng)
        
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

            # Add connected synapses to each neuron (full model of connectivity)
            post.in_syn_list.append(syn)

        #####################################################################
        # TODO --> Check how this is supposed to work with Nick or Adnan 
        #####################################################################
        # Determine if an input needs to be connected to a neuron
        elif line[0] == 'INPUT':
            #print('Input is connected to', line[2])
            neuron = neuron_dict[line[2]]
            index = count
            count += 1 # TODO --> FIX THIS (Or rather just don't use it)
            input_synapse = inp_class.input_synapse_list[index]
            input_synapse.post = neuron
            neuron.in_syn_list.append(input_synapse)
            synapse_list.append(input_synapse)



        # A hacky way to stop reading network components  <-- TODO --> FIX THIS
        elif line[0] == '#':
            #print('Finished reading network')
            break

        # Default case to catch all other lines
        else:
            pass


    # Print out the connectivity of the network
    #print('--------------------')
    #for neuron in neuron_dict:
    #    print(neuron_dict[neuron].name)
    #    for synapse in neuron_dict[neuron].in_syn_list:
    #        print('  ', synapse.pre.name, '->', synapse.post.name)
    #print('--------------------')


    # Create a chaotic RNG instance
    #rng = Chaos_RNG('lookup_geo_5_4.tbl', 0.1, 0.775)
    #rng = Std_RNG()
    #rng.step()
    #print(rng.get_num_out())

    # Use the -1 for now because we are setting clk+1 a few places in the simulation
    # Synapses are processed before neurons because synapse activity is instantaneous
    # whereas neuron outputs are buffered by a DFF
    for clk in range(inp_class.SIM_CYCLES-2):
        for synapse in synapse_list:
            synapse.shift_spikes(clk)
        for neuron in neuron_dict:
            neuron_dict[neuron].accum(clk)
        rng.step()
        #print(rng.get_num_out())
        

    np.set_printoptions(precision=2)

    # print('--------------------')
    output = neuron_dict['O0'].fire[14]
    label = labels[inp_class.inp_num-1]
    
    #print(int(output))

    if output == 1 and label == 'T':
        #print("Correctly classified")
        num_correct += 1
    elif output == 1 and label != 'T':
        #print("Incorrectly classified")
        pass
    elif output == 0 and label == 'T':
        #print("Incorrectly classified")
        pass
    elif output == 0 and label != 'T':
        #print("Correctly classified")
        num_correct += 1
    else:
        print("OUCH")

print("Done!")
print("{0}/{1}: {2}".format(num_correct, len(labels), num_correct/len(labels)))
