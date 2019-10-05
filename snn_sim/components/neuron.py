import params
import numpy as np

class InputNeuron:
    def __init__(self, name="", fire=[]):
        """Creates a pseudo-neuron to stimulate a network with digital inputs.

        Args:
            name - A string uniquely identifying the neuron.
            fire - An input stimulus array for this neuron.
        """
        self.name = str(name)
        self.fire = fire


class IntegrateAndFire:
# TODO --> Avoid accessing arrays at "clk+1" index
    def __init__(self, name="", Vmem=params.get("Vrst"), Vth=params.get("Vth"), rf=0, cap=params.get("cap")):
        """Creates an Integrate-and-Fire neuron with the given parameters.

        Args:
            name - A string uniquely identifying the neuron.
            Vmem - The initial value of the membrane voltage.
            Vth  - The threshold of the neuron.
            rf   - The refractory period of the neuron (in cycles).
            cap  - The membrane capacitance of the neuron.
        """
        self.name = str(name)
        self.Vth = Vth
        self.tper = params.get("tper")
        self.VDD = params.get("VDD")
        self.VSS = params.get("VSS")
        self.GND = (self.VDD - self.VSS)/2 + self.VSS
        self.cycles = params.get("cycles")
        self.Cmem = cap
        self.refractory = rf
        self.refractory_cycles_left = 0
        self.input_synapses = []

        # Neuron state information
        self.Vmem = np.ones(self.cycles) * Vmem
        self.fire = np.zeros(self.cycles)

    def reset(self):
        self.Vmem = np.ones(self.cycles) * self.GND
        self.fire = np.zeros(self.cycles)
        self.refractory_cycles_left = 0

    def accumulate(self, clk):
        if self.refractory_cycles_left > 0:
            self.refractory_cycles_left -= 1
            # TODO --> When the neuron is FIRING or IDLE
            return
        
        for synapse in self.input_synapses:
            if synapse.activity[clk] != 0:

                # TODO --> When the neuron is ACCUMULATING

                delta_Vmem = self.tper * synapse.activity[clk] / self.Cmem
                self.Vmem[clk] -= delta_Vmem
                if self.Vmem[clk] < self.VSS:
                    self.Vmem[clk] = self.VSS
                if self.Vmem[clk] > self.VDD:
                    self.Vmem[clk] = self.VDD
                if self.Vmem[clk] < self.Vth:
                    self.fire[clk+1] = 1
                    self.Vmem[clk+1] = self.GND
                    self.refractory_cycles_left = self.refractory
                    return
            
            # TODO --> When the neuron is IDLE
            else:
                pass

        # Keeps accumulation of Vmem updated
        self.Vmem[clk+1] = self.Vmem[clk]


class IntegrateAndFire2:
# TODO --> Avoid accessing arrays at "clk+1" index
    def __init__(self, name="", refractory=0, cap=params.get("cap")):
        """Creates an Integrate-and-Fire neuron with the given parameters.

        Args:
            name - A string uniquely identifying the neuron.
            Vmem - The initial value of the membrane voltage.
            Vth  - The threshold of the neuron.
            rf   - The refractory period of the neuron (in cycles).
            cap  - The membrane capacitance of the neuron.
        """
        self.name = str(name)
        self.Vth = params.get("Vth")
        self.tper = params.get("tper")
        self.VDD = params.get("VDD")
        self.VSS = params.get("VSS")
        self.MID = (self.VDD - self.VSS)/2 + self.VSS
        self.cycles = params.get("cycles")
        self.Cmem = cap
        self.refractory = refractory
        self.refractory_cycles_left = 0

        # Neuron state information
        self.Vmem = np.ones(self.cycles) * self.MID
        self.fire = np.zeros(self.cycles)

    def reset(self):
        self.Vmem = np.ones(self.cycles) * self.MID
        self.fire = np.zeros(self.cycles)
        self.refractory_cycles_left = 0

    def accumulate(self, clk, input_current):
        if self.refractory_cycles_left > 0:
            self.refractory_cycles_left -= 1
            # TODO --> When the neuron is FIRING or IDLE
            return 0
       
        # TODO --> When the neuron is ACCUMULATING or IDLE (is current 0 or not?)

        delta_Vmem = self.tper * input_current / self.Cmem
        self.Vmem[clk] -= delta_Vmem
        if self.Vmem[clk] < self.VSS:
            self.Vmem[clk] = self.VSS
        if self.Vmem[clk] > self.VDD:
            self.Vmem[clk] = self.VDD
        if self.Vmem[clk] < self.Vth:
            # TODO --> Index out of bounds errors?
            #          Adding a simple flip flop could fix this
            self.fire[clk+1] = 1
            self.Vmem[clk+1] = self.MID
            self.refractory_cycles_left = self.refractory
            return 1

        # TODO --> Leak term to make LIF??

        # Keeps accumulation of Vmem updated
        self.Vmem[clk+1] = self.Vmem[clk]
        return 0

