import sys
from snn_components import *

import matplotlib.pyplot as plt

network_file = sys.argv[1]
print(network_file)

input_file = sys.argv[2]
print(input_file)

# if network == 1:
#     textfile = open("../smallnetdesc.txt", "r")
# else:
#     textfile = open("../shape_recog_net.txt", "r")


# Read the input file into a list of lines
with open(input_file, 'r') as f:
    lines = f.readlines()
# print(len(lines))


input_neuron_list = []
input_synapse_list = []

# Create "input neurons/synapses" to carry input spikes into the network
for line in lines:
    line = line.replace(' \n', '')
    line = line.replace('\n', '')
    # print(line)
    line = line.split(' ')
    # print(line)
    line = [int(i) for i in line]
    # print(line)
    # exit()

    # input_neuron = inNeu(line, "STR")
    # input_synapse = inSyn(Mp_in, Mn_in, 0, input_neuron)

    # Create an input neuron and synapse, the post-neuron of the synapse is as yet unknown
    input_neuron = InputNeuron(line, "INP")
    # input_synapse = InputSynapse(Mp_in, Mn_in, 0, input_neuron, None)
    input_synapse = Synapse(Mp_in, Mn_in, 0, input_neuron, None)
    input_neuron_list.append(input_neuron)
    input_synapse_list.append(input_synapse)

    print(np.array(line))

SIM_CYCLES = len(line)
print(SIM_CYCLES)




# Read the network file into a list of lines
with open(network_file, 'r') as f:
    lines = f.readlines()
# print(len(lines))
# exit()

neuron_dict = {}
synapse_list = []

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
        neuron_dict[name] = Neuron(name, Vmem, threshold, refractory)
    
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
        print('Input is connected to', line[2])
        neuron = neuron_dict[line[2]]
        # index = int(line[1])
        index = count
        count += 1
        input_synapse = input_synapse_list[index]
        input_synapse.post = neuron
        neuron.in_syn_list.append(input_synapse)
        synapse_list.append(input_synapse)



    # A hacky way to stop reading network components  <-- TODO --> FIX THIS
    elif line[0] == '#':
        print('Finished reading network')
        break

    # Default case to catch all other lines
    else:
        pass

# TODO --> Use this section for updated neuron/synapse model (full connectivity)
# Add connected synapses to each neuron

# for synapse in synapse_list:
#     neuron = synapse.post
#     neuron.in_syn_list.append(synapse)

# Print out the connectivity of the network
print('--------------------')
for neuron in neuron_dict:
    print(neuron_dict[neuron].name)
    for synapse in neuron_dict[neuron].in_syn_list:
        print('  ', synapse.pre.name, '->', synapse.post.name)
print('--------------------')


# Use the -1 for now because we are setting clk+1 a few places in the simulation
# Synapses are processed before neurons because synapse activity is instantaneous
# whereas neuron outputs are buffered by a DFF
for clk in range(SIM_CYCLES-1):
    for synapse in synapse_list:
        # print(synapse.pre.name)
        synapse.shift_spikes(clk)
    for neuron in neuron_dict:
        neuron_dict[neuron].accum(clk)
        # print(neuron_dict[neuron].name)
    

np.set_printoptions(precision=2)
# for synapse in synapse_list:
#     print('Pre-name:', synapse.pre.name)
#     print('    Activity: ', synapse.activity)
#     print('    Post-Vmem:', synapse.post.Vmem)
#     print('    Post-fire:', synapse.post.fire)

# Print and plot some results to check functionality of network
# print('O03 fire:', neuron_dict['O03'].fire)
# print('O03 Vmem:', neuron_dict['O03'].Vmem)
# print('I07 fire:', neuron_dict['I07'].fire)
# print('I07 Vmem:', neuron_dict['I07'].Vmem)

# plt.figure()
# plt.subplot(311)
# plt.plot(neuron_dict['O01'].fire)

# plt.subplot(312)
# plt.plot(neuron_dict['O02'].fire)

# plt.subplot(313)
# plt.plot(neuron_dict['O03'].fire)

# plt.figure()
# plt.subplot(711)
# plt.plot(neuron_dict['I01'].fire)
# plt.subplot(712)
# plt.plot(neuron_dict['I02'].fire)
# plt.subplot(713)
# plt.plot(neuron_dict['I03'].fire)
# plt.subplot(714)
# plt.plot(neuron_dict['I04'].fire)
# plt.subplot(715)
# plt.plot(neuron_dict['I05'].fire)
# plt.subplot(716)
# plt.plot(neuron_dict['I06'].fire)
# plt.subplot(717)
# plt.plot(neuron_dict['I07'].fire)

# plt.show()


# print('I0 fire:', neuron_dict['I0'].fire)
# print('I0 Vmem:', neuron_dict['I0'].Vmem)
# print()
# print('I1 fire:', neuron_dict['I1'].fire)
# print('I1 Vmem:', neuron_dict['I1'].Vmem)
# print()

# print(neuron_dict['O0'].in_syn_list[0].activity)
# print(neuron_dict['O0'].in_syn_list[1].activity)
# print(neuron_dict['O0'].in_syn_list[2].activity)


print('H2 threshold:', neuron_dict['H2'].Vth)
print('H2 fire:', neuron_dict['H2'].fire)
print('H2 Vmem:', neuron_dict['H2'].Vmem)


print('O0 fire:', neuron_dict['O0'].fire)
print('O0 Vmem:', neuron_dict['O0'].Vmem)

print(Vrst)
h2 = neuron_dict['H2']
print(h2.fire[10:23])
print(h2.Vmem[17])
