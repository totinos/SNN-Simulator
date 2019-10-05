import params
import numpy as np

#from params import LRS, HRS, cycles, Vdiff

class TwinMemristive:
    def __init__(self, Mp=params.get("LRS"), Mn=params.get("HRS"), delay=0, pre=None, post=None):
        self.Mp = Mp
        self.Mn = Mn
        self.delay = delay
        self.pre = pre
        self.post = post
        self.Gmax = 1/params.get("LRS") - 1/params.get("HRS")
        self.G = np.ones(params.get("cycles")) * self.Gmax
        self.activity = np.zeros(params.get("cycles"))
        
        self.VDD = params.get("VDD")
        self.VSS = params.get("VSS")
        self.GND = (self.VDD - self.VSS)/2 + self.VSS

    def reset(self):
        self.G = np.ones(params.get("cycles")) * self.Gmax
        self.activity = np.zeros(params.get("cycles"))

    def propagate_spikes(self, clk):
# TODO --> Avoid accessing "clk+1" index or higher
# TODO --> Use self.G[clk+self.delay] for conductance
        if (self.pre is not None):
            current = (self.VDD - self.GND) * self.G[clk]
            #print("current:", current)
            self.activity[clk+self.delay] = self.pre.fire[clk] * current
            #print("activity cycle:", clk+self.delay)
            #print("activity:", self.pre.fire[clk] * current)

class TwinMemristive2:
    def __init__(self, Mp=params.get("LRS"), Mn=params.get("HRS"), delay=0):
        self.Mp = Mp
        self.Mn = Mn
        self.delay = delay
        self.VDD = params.get("VDD")
        self.VSS = params.get("VSS")
        self.MID = (self.VDD - self.VSS)/2 + self.VSS
        self.cycles = params.get("cycles")
        self.G = np.ones(self.cycles) * (1/self.Mp - 1/self.Mn)
        self.activity = np.zeros(self.cycles)

    def reset(self):
        # TODO --> self.Mp & Mn will likely not be initial values after learning
        self.G = np.ones(self.cycles) * (1/self.Mp - 1/self.Mn)
        self.activity = np.zeros(self.cycles)

    # TODO --> Index out of bounds errors w/ accessing clk+delay??
    def propagate_spikes(self, clk, input_fire):
        current = (self.VDD - self.MID) * self.G[clk]
        self.activity[clk+self.delay] = input_fire * current
        return self.activity[clk]
