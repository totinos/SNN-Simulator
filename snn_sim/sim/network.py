import numpy as np
import matplotlib.pyplot as plt

import networkx as nx

import argparse

import params

from components.synapse import TwinMemristive as TM
from components.neuron import IntegrateAndFire as IAF
from components.neuron import InputNeuron as IN

from components.synapse import TwinMemristive2 as TM2
from components.neuron import IntegrateAndFire2 as IAF2

class Network:
    def __init__(self):
        self.neuron_dict = {}
        self.synapse_list = []
        self.input_arrays = []

        self.net = nx.DiGraph()
    
    def define_inputs(self, input_file):
        with open(input_file, "r") as f:
            lines = f.readlines()
        for line in lines:
            line = line.replace(" \n", "")
            line = line.replace("\n", "")
            line = line.split(" ")
            line = [int(i) for i in line]
            self.input_arrays.append(line)
    
    def print_inputs(self):
        for line in self.input_arrays:
            print(line)

    def build(self, network_file):
        with open(network_file, "r") as f:
            lines = f.readlines()
        HRS, LRS = params.get("HRS", "LRS")
        # TODO --> Fix the indexing here
        for line in lines[1:18]:
            line = line.replace("\n", "")
            line = line.split(" ")

            # Read in a network
            if line[0] == "+":
                if line[1] == "I":
                    print("N: I")
                elif line[1] == "O":
                    print("N: O")
                
                unique_id = line[2]
                threshold = line[3]
                # TODO --> Fix the threshold calculation here
                threshold = 599e-3
                x = line[4]
                y = line[5]
                z = line[6]
                self.neuron_dict[unique_id] = IAF(name=unique_id, Vth=threshold, rf=1)

                if line[1] == "I":
                    input_neuron = IN("Input", self.input_arrays[int(unique_id)])
                    input_synapse = TM(Mp=LRS, Mn=HRS, delay=0, pre=input_neuron, post=self.neuron_dict[unique_id])
                    self.synapse_list.append(input_synapse)
                    self.neuron_dict[unique_id].input_synapses.append(input_synapse)
                else:
                    pass

            elif line[0] == "|":
                pre = self.neuron_dict[line[3]]
                post = self.neuron_dict[line[4]]
                delay = int(line[5])
                mbits = int(line[6])
                Mp = LRS if mbits & 1 == 1 else HRS
                Mn = HRS if (mbits >> 1) & 1 == 1 else LRS
                syn = TM(Mp, Mn, delay, pre, post)
                self.synapse_list.append(syn)
                post.input_synapses.append(syn)

            else:
                pass

    def build_from_file(self, network_file):
        with open(network_file, "r") as f:
            lines = f.readlines()
        HRS, LRS = params.get("HRS", "LRS")

        for line in lines[1:18]:
            line = line.replace("\n", "")
            line = line.split(" ")

            # Read a network
            if line[0] == "+":
                if line[1] == "I":
                    print("N: I")
                elif line[1] == "O":
                    print("N: O")

                unique_id = line[2]
            elif line[0] == "|":
                pass
            else:
                pass

    # TODO --> Add neurons and synapses to the network
    # TODO --> Maybe this should be separate functions (add_synapse & add_neuron)?
    def add(self):
        pass

    # TODO --> Should this be here??????
    def prune(self):
        pass

    def viz(self):
        pass

    def print_connectivity(self):
        print("----------")
        for key, neuron in self.neuron_dict.items():
            print(neuron.name)
            for synapse in neuron.input_synapses:
                print("  ", synapse.pre.name, "-->", synapse.post.name)
        print("----------")

    def run(self):
        SIM_CYCLES = len(self.input_arrays[0])
        print(SIM_CYCLES)
        for clk in range(SIM_CYCLES):
            for synapse in self.synapse_list:
                synapse.propagate_spikes(clk)
            for key, neuron in self.neuron_dict.items():
                neuron.accumulate(clk)

    def reset(self):
        for synapse in self.synapse_list:
            synapse.reset()
        for key, neuron in self.neuron_dict.items():
            neuron.reset()

    # TODO --> This is hardcoded for now, change it
    def plot(self):
        plot_spikes(self.input_arrays[0], self.input_arrays[1], self.input_arrays[2], self.input_arrays[3], self.input_arrays[4], self.neuron_dict["5"].fire, self.neuron_dict["6"].fire, self.neuron_dict["7"].fire)

        

def plot_spikes(*args):

    max_len = 0
    num_waveforms = len(args)
    waveforms = []

    for arg in args:
#             if not isinstance(arg, list):
#                 print("ERROR OCCURRED DURING PLOTTING")
#                 return 
        data = np.repeat(arg, 2)
        if (len(data) > max_len):
            max_len = len(data)
        waveforms.append(data)

    # Set up time axis and clock signal
    clock = 1 - np.arange(max_len) % 2
    t = 0.5 * np.arange(max_len)

    # Append 0s to signals that are shorter than the longest signal
    for i in range(len(waveforms)):
        len_diff = max_len - len(waveforms[i])
        if len_diff > 0:
            waveforms[i] = np.append(waveforms[i], np.zeros(len_diff))

    # Reverse order of signals so first argument is top signal (below clock)
    waveforms = np.flip(waveforms, 0)

    # Plot the signals
    for i in range(len(waveforms)):
        plt.step(t, waveforms[i] + 2*i, where="post")
    plt.step(t, clock + 2*num_waveforms, where="post")
    plt.show()
    return
