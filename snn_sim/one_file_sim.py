
import numpy as np
from optparse import OptionParser



params = {
    "VDD": 1.2,
    "VSS": 0,
    "cycles": 20,
    "tper": 5e-08,
    "Vth": 0.55,
    "cap": 9e-12,
    "HRS": 300000.0,
    "LRS": 30000.0,
    "Vrst": 0.6
}

class InputNeuron:
    """Implements a pseudo-neuron that stimulates a network with digital inputs."""
    
    def __init__(self, name="", fire=[]):
        """Creates a pseudo-neuron to stimulate a network.

        Args:
            name - A string uniquely identifying the neuron.
            fire - An input stimulus array for this neuron.
        """
        self.name = str(name)
        self.fire = fire

class Neuron:
    """Implements an Integrate-and-Fire neuron."""

    def __init__(self, name="", Vth=params["Vth"], rf=0):
        """Creates an Integrate-and-Fire neuron with the given parameters.

        Args:
            name - A string uniquely identifying the neuron.
            Vmem - The initial value of the membrane voltage.
            Vth  - The threshold of the neuron.
            rf   - The refractory period of the neuron (in cycles).
            cap  - The membrane capacitance of the neuron.
        """
        self.name = str(name)
        self.Vth = params["Vrst"] - (Vth*params["Vrst"])
        self.Cmem = params["cap"]
        self.refractory = rf
        self.refractory_cycles_left = 0
        self.input_synapses = []

        self.Vmem = np.ones(params["cycles"]) * params["Vrst"]
        self.fire = np.zeros(params["cycles"])

        self.firing_flop_state = 0

    def reset(self):
        """Resets the internal dynamics of the neuron.
        """
        self.Vmem = np.ones(params["cycles"]) * params["Vrst"]
        self.fire = np.zeros(params["cycles"])
        self.refractory_cycles_left = 0

    # TODO --> Add checks to ensure this function is called ONLY for consecutive clock cycles
    def accumulate(self, clk):
        """Updates the internal state variables of the neuron.
        
        Modifies the membrane potential according to the inputs from
        connected synapses. Queues firing events and determines the
        neuron's refractory behavior.
        
        Args:
            clk - The current clock cycle of the simulator.
        """
        
        # Preserve Vmem from previous cycle
        self.Vmem[clk] = params["Vrst"] if clk == 0 else self.Vmem[clk-1]

        # Check the state of the firing flop to see if fire is queued
        if self.firing_flop_state == 1:
            self.firing_flop_state = 0
            # TODO --> This is how I want to evaluate the fire of the neuron, but I need
            #          to reorder the neuron/synapse processing in order to make it work.
            # TODO --> Check to make sure the neuron can have refractory period of 0.
            #self.fire[clk] = 1
            self.Vmem[clk] = params["Vrst"]

        # Check to see if the neuron is in its refractory period
        if self.refractory_cycles_left > 0:
            self.refractory_cycles_left -= 1
            # TODO --> When the neuron is FIRING or IDLE
        
        # The neuron accumulates incoming signals
        else:

            for synapse in self.input_synapses:
                if self.name == "H1":
                    print(self.input_synapses[4].pre.name)
                    print(self.name, ": from", synapse.pre.name, "=", synapse.activity[clk])
                if synapse.activity[clk] != 0:
                    # TODO --> When the neuron is ACCUMULATING
                    delta_Vmem = params["tper"] * synapse.activity[clk] / self.Cmem
                    self.Vmem[clk] -= delta_Vmem
                    if self.Vmem[clk] < params["VSS"]:
                        self.Vmem[clk] = params["VSS"]
                    if self.Vmem[clk] > params["VDD"]:
                        self.Vmem[clk] = params["VDD"]
                    if self.Vmem[clk] < self.Vth:
                        # TODO --> This sets the value of fire one clock cycle too far in advance,
                        #          but that is the only reason the synapses can track it. Maybe
                        #          try reordering the operations so that the neurons are processed
                        #          before the synapses? This might help. Think through this though,
                        #          as the elements are essentially co-dependent.
                        self.fire[clk+1] = 1
                        self.firing_flop_state = 1
                        self.refractory_cycles_left = self.refractory
            
                # TODO --> When the neuron is IDLE
                else:
                    pass

class Synapse:
    """ Implements a Twin-Memristive synapse."""

    def __init__(self, name="", Mp=params["LRS"], Mn=params["HRS"], delay=0, pre=None, post=None):
        """Creates a Twin-Memristive Synapse with the given parameters.

        Args:
            name  - A string uniquely identifying the synapse.
            Mp    - A numeric value representing positive memristance.
            Mn    - A numeric value representing negative memristance.
            delay - The delay of the synapse (in cycles).
            pre   - The neuron before this synapse.
            post  - The neuron after this synapse.
        """
        self.name = str(name)
        self.Mp = Mp
        self.Mn = Mn
        self.delay = [0]*(delay*2)
        self.pre = pre
        self.post = post
        self.G_init = 1/self.Mp - 1/self.Mn
        self.G = np.ones(params["cycles"]) * self.G_init
        self.activity = np.zeros(params["cycles"], dtype='float')

    def reset(self):
        """Resets the internal dynamics of the synapse.
        """
        # TODO --> self.Mp & Mn will likely not be initial values after learning
        self.G = np.ones(params["cycles"]) * self.G_init
        self.activity = np.zeros(params["cycles"])

    def propagate_spikes(self, clk):
        """Updates the internal state variables of the synapse.
        
        Shifts spikes through the synapse according to the delay and
        determines the current through the synapse at each clock cycle
        according to the weight dictated by the memristances Mp and Mn.

        Args:
            clk - The current clock cycle of the simulator.
        """
        delay_len = len(self.delay)
        
        if self.post.name == "H1":
            print(delay_len)
            if self.pre.name == "I4":
                print(self.pre.fire)
                print(clk, self.pre.fire[clk])
        

        current = (params["VDD"] - params["Vrst"]) * self.G[clk]
        processed_spike = self.pre.fire[clk]
        # print(self.pre.name)
        # print(self.pre.fire)
        # print(self.pre.fire[clk])
        # print(processed_spike)
        # print()

        if delay_len > 0:
            processed_spike = self.delay[delay_len-1]
            for i in reversed(range(1, delay_len)):
                self.delay[i] = self.delay[i-1]
            self.delay[0] = self.pre.fire[clk]
        
        self.activity[clk] = processed_spike * current
        if self.post.name == "H1":
            print(self.delay)
            print(self.pre.name, "--->", self.pre.fire[clk], "--->", self.activity[clk])

        # TODO --> Determine whether the synapse is idle or active here


#####################################################################
#                                                                   #
#  Read in a network and some digital inputs, simulate the network  #
#                                                                   #
#####################################################################

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--nf", dest="network_file", help="Network description file", metavar="NET_FILE")
    parser.add_option("--if", dest="input_file", help="Input description file", metavar="IN_FILE")
    (options, args) = parser.parse_args()
    if not options.network_file:
        parser.error("Network file not specified")
    if not options.input_file:
        parser.error("Input file not specified")
  

    input_neuron_list = []
    input_synapse_list = []
    neuron_dict = {}
    synapse_list = []


    #
    # Read the input file
    #
    with open(options.input_file, "r") as f:
        lines = f.read().splitlines()
    for line in lines:
        line = line.split(" ")
        line = [int(i) for i in line]
        input_neuron = InputNeuron(name="INP", fire=line)
        input_synapse = Synapse(name="IS", delay=0, pre=input_neuron, post=None)
        input_neuron_list.append(input_neuron)
        input_synapse_list.append(input_synapse)

    SIM_CYCLES = len(line)
    count = 0

    #
    # Read the network file
    #
    with open(options.network_file, "r") as f:
        lines = f.read().splitlines()
    for line in lines:
        line = line.split(" ")

        if line[0] == "N":
            name = line[1]
            threshold = float(line[2])
            refractory = int(line[3])
            neuron_dict[name] = Neuron(name=name, Vth=threshold, rf=refractory)
        elif line[0] == "S":
            pre = neuron_dict[line[1]]
            post = neuron_dict[line[2]]
            Geff = float(line[3])
            delay = int(line[4])
            wp = float(line[5])*1e3
            wn = float(line[6])*1e3
            syn = Synapse(name="S", Mp=wp, Mn=wn, delay=delay, pre=pre, post=post)
            synapse_list.append(syn)
            post.input_synapses.append(syn)
        elif line[0] == "INPUT":
            neuron = neuron_dict[line[2]]
            index = count
            count += 1 # TODO --> THIS CAN BE MADE BETTER
            input_synapse = input_synapse_list[index]
            input_synapse.post = neuron
            neuron.input_synapses.append(input_synapse)
            synapse_list.append(input_synapse)
        elif line[0] == "#":
            break

    for clk in range(SIM_CYCLES):
        for synapse in synapse_list:
            synapse.propagate_spikes(clk)
        for key, neuron in neuron_dict.items():
            neuron.accumulate(clk)
        print()

    for key, neuron in neuron_dict.items():
        print(neuron.name)
        for synapse in neuron.input_synapses:
            print("  ", synapse.pre.name, "->", synapse.post.name)


    output = neuron_dict["O0"].fire[14]
    print(output)
    print("I0:", neuron_dict["I0"].fire)
    print("I1:",neuron_dict["I1"].fire)
    print("I2:",neuron_dict["I2"].fire)
    print("I3:",neuron_dict["I3"].fire)
    print("I4:",neuron_dict["I4"].fire)
    #print("I0->H0:", neuron_dict["H0"].input_synapses[0].activity[0])
    #print("I1->H0:", neuron_dict["H0"].input_synapses[1].activity)
    #print("I2->H0:", neuron_dict["H0"].input_synapses[2].activity)
    #print("I3->H0:", neuron_dict["H0"].input_synapses[3].activity)
    #print("I4->H0:", neuron_dict["H0"].input_synapses[4].activity[0])
    print("I4 --> H0 Activity", neuron_dict["H0"].input_synapses[4].activity)
    print("H0 Vmem:",neuron_dict["H1"].Vmem)
    print("H0 fire:",neuron_dict["H1"].fire)
    print("Output:", neuron_dict["O0"].fire)


    exit()
   
    inputs = [0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0]
    input_neuron = InputNeuron("IN", inputs)
    input_synapse = Synapse(name="IS", delay=0, pre=input_neuron, post=None)
    neuron = Neuron(name="N", rf=1)
    neuron.input_synapses.append(input_synapse)
    input_synapse.post = neuron

    SIM_CYCLES = len(inputs)
    print("SIM_CYCLES:", SIM_CYCLES)
    print("Inputs:", input_neuron.fire)

    for clk in range(SIM_CYCLES):
        input_synapse.propagate_spikes(clk)
        neuron.accumulate(clk)

    print("Neuron Vmem:", neuron.Vmem)
    print("Neuron output:", neuron.fire)

    
