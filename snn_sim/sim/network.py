import numpy as np
import argparse

import params

from components.synapse import TwinMemristive as TM
from components.neuron import IntegrateAndFire as IAF
from components.neuron import InputNeuron as IN

class Network:
    def __init__(self):
        self.neuron_dict = {}
        self.synapse_list = []
        self.input_arrays = []
    
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
                threshold = 599e-3
                x = line[4]
                y = line[5]
                z = line[6]
                self.neuron_dict[unique_id] = IAF(name=unique_id, Vth=threshold, rf=1)

                if line[1] == "I":
                    input_neuron = IN("Input", self.input_arrays[int(unique_id)])
                    input_synapse = TM(Mp=LRS, Mn=HRS, delay=0, pre=input_neuron, post=self.neuron_dict[unique_id])
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


                print("S")
            else:
                print("other...")

    def print_connectivity(self):
        print("----------")
        for key, neuron in self.neuron_dict.items():
            print(neuron.name)
            for synapse in neuron.input_synapses:
                print("  ", synapse.pre.name, "-->", synapse.post.name)
        print("----------")

    def run(self):
        pass

    def reset(self):
        pass

    def plot(self):
        pass

