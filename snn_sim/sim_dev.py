import sys
import collections
from snn_components import *

import matplotlib.pyplot as plt

network_file = sys.argv[1]
#print(network_file)

input_file = sys.argv[2]
#print(input_file)

# if network == 1:
#     textfile = open("../smallnetdesc.txt", "r")
# else:
#     textfile = open("../shape_recog_net.txt", "r")


# Read the input file into a list of lines
with open(input_file, 'r') as f:
    lines = f.readlines()

input_neuron_list = []
input_synapse_list = []

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
    input_neuron_list.append(input_neuron)
    input_synapse_list.append(input_synapse)

    #print(np.array(line))

SIM_CYCLES = len(line)
#print(SIM_CYCLES)




# Read the network file into a list of lines
with open(network_file, 'r') as f:
    lines = f.readlines()
# print(len(lines))
# exit()

neuron_dict = {}
synapse_list = []
rng = Std_RNG()
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
        neuron_dict[name] = Neuron(name, Vmem, threshold, refractory, stochastic=True, rng=rng)
    
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
        input_synapse = input_synapse_list[index]
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
print('--------------------')
for neuron in neuron_dict:
    print(neuron_dict[neuron].name)
    for synapse in neuron_dict[neuron].in_syn_list:
        print('  ', synapse.pre.name, '->', synapse.post.name)
print('--------------------')


# Create a chaotic RNG instance
#rng = Chaos_RNG('lookup_geo_5_4.tbl', 0.1, 0.775)
#rng = Std_RNG()
#rng.step()
#print(rng.get_num_out())

# Use the -1 for now because we are setting clk+1 a few places in the simulation
# Synapses are processed before neurons because synapse activity is instantaneous
# whereas neuron outputs are buffered by a DFF
for clk in range(SIM_CYCLES-2):
    for synapse in synapse_list:
        synapse.shift_spikes(clk)
    for neuron in neuron_dict:
        neuron_dict[neuron].accum(clk)
    rng.step()
    

np.set_printoptions(precision=2)


###########################################################
# This section is for testing iris network
###########################################################

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


###########################################################
# This section is for testing shape recognition network
###########################################################

# print('I0 fire:', neuron_dict['I0'].fire)
# print('I0 Vmem:', neuron_dict['I0'].Vmem)
# print()
# print('I1 fire:', neuron_dict['I1'].fire)
# print('I1 Vmem:', neuron_dict['I1'].Vmem)
# print()

# print(neuron_dict['O0'].in_syn_list[0].activity)
# print(neuron_dict['O0'].in_syn_list[1].activity)
# print(neuron_dict['O0'].in_syn_list[2].activity)


# H0 = neuron_dict['H0']
# print('H0 threshold:', H0.Vth)
# print()
# print('H0 fire:', H0.fire)
# print()
# print('H0 Vmem:', H0.Vmem)
# print()


# H1 = neuron_dict['H1']
# print('H1 threshold:', H1.Vth)
# print()
# print('H1 fire:', H1.fire)
# print()
# print('H1 Vmem:', H1.Vmem)
# print()


# H2 = neuron_dict['H2']
# print('H2 threshold:', H2.Vth)
# print()
# print('H2 fire:', H2.fire)
# print()
# print('H2 Vmem:', H2.Vmem)
# print()


# O0 = neuron_dict['O0']
# print('O0 threshold:', O0.Vth)
# print()
# print('O0 fire:', O0.fire)
# print()
# print('O0 Vmem:', O0.Vmem)
# print()


# O0 = neuron_dict['O0']
# print('O0 fire:', O0.fire)
# print('O0 Vmem:', O0.Vmem)


###########################################################
# This section is for testing test_net network
###########################################################


# print()
# I0 = neuron_dict['I0']
# print('I0 threshold:', I0.Vth)
# print('I0 fire:', I0.fire)
# print('I0 Vmem:', I0.Vmem)
# print()

# I1 = neuron_dict['I1']
# print('I1 threshold:', I1.Vth)
# print('I1 fire:', I1.fire)
# print('I1 Vmem:', I1.Vmem)  
# print()

# I2 = neuron_dict['I2']
# print('I2 threshold:', I2.Vth)
# print('I2 fire:', I2.fire)
# print('I2 Vmem:', I2.Vmem)  
# print()

# I3 = neuron_dict['I3']
# print('I3 threshold:', I3.Vth)
# print('I3 fire:', I3.fire)
# print('I3 Vmem:', I3.Vmem)  
# print()

# I4 = neuron_dict['I4']
# print('I4 threshold:', I4.Vth)
# print('I4 fire:', I4.fire)
# print('I4 Vmem:', I4.Vmem)  
# print()

# H0 = neuron_dict['H0']
# print('H0 threshold:', H0.Vth)
# print('H0 fire:', H0.fire)
# print('H0 Vmem:', H0.Vmem)
# print()

# H1 = neuron_dict['H1']
# print('H1 threshold:', H1.Vth)
# print('H1 fire:', H1.fire)
# print('H1 Vmem:', H1.Vmem)
# print()

# H2 = neuron_dict['H2']
# print('H2 threshold:', H2.Vth)
# print('H2 fire:', H2.fire)
# print('H2 Vmem:', H2.Vmem)
# print()

# O0 = neuron_dict['O0']
# print('O0 threshold:', O0.Vth)
# print('O0 fire:', O0.fire)
# print('O0 Vmem:', O0.Vmem)

# # print()
# # print("O0 Output for each shape:")
# # for i in range(5):
# #     print("  ", end="")
# #     for j in range(14):
# #         print("{} ".format(O0.fire[i*j + j]), end="")
# #     print()

# for synapse in synapse_list:
#     if (synapse.pre.name == "H0" or synapse.pre.name == "H1") and synapse.post.name == "O0":
#         print(synapse.pre.name, "->", synapse.post.name)
#         print(synapse.delay)
#         print("    synapse activity:  {}".format(synapse.activity))
#     if (synapse.pre.name == "I4") and synapse.post.name == "H0":
#         print(synapse.pre.name, "->", synapse.post.name)
#         print(synapse.delay)
#         print("    synapse activity:  {}".format(synapse.activity))


###########################################################
# This section is for printing neuron phase information
###########################################################

# print()
# print(neuron_dict['I3'].power_stages)
# print(neuron_dict['I3'].fire)
# input_idle = 0
# input_accum = 0
# input_fire = 0
# idle = 0
# accum = 0
# fire = 0
# for index in neuron_dict:
#     neuron = neuron_dict[index]
#     stages = collections.Counter(neuron.power_stages)
#     if neuron.name[0] == 'I':
#         input_idle += stages['I']
#         input_accum += stages['A']
#         input_fire += stages['F']
#         print(input_idle, input_accum, input_fire)
#     else:
#         idle += stages['I']
#         accum += stages['A']
#         fire += stages['F']
#         print(idle, accum, fire)

# print("SIM_CYCLES", SIM_CYCLES)
# print()
# print()
# print("Neuron power-consumption stages:")
# print("Input Neurons Only:")
# print("  Idle:", input_idle)
# print("  Accum:", input_accum)
# print("  Fire:", input_fire)
# print()
# print("Internal Neurons Only:")
# print("  Idle:", idle)
# print("  Accum:", accum)
# print("  Fire:", fire)
# print()
# print("Total:")
# print("  Idle:", input_idle + idle)
# print("  Accum:", input_accum + accum)
# print("  Fire:", input_fire + fire)

# print()
# print()


# print('--------------------')
print(int(neuron_dict['O0'].fire[14]))
