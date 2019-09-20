import numpy as np

class RNG:
    def __init__(self):
        self.output = 0
    
    def step(self):
        self.output = np.random.randint(8)
    
    def get_output(self):
        return self.output

class Chaotic_RNG:
    def __init__(self, lookup_table, Vseed, Vbias):
        data = np.genfromtxt(lookup_table)
        self.chaos = {}
        for i in range(len(data)):
            key = tuple((data[i][0], data[i][1]))
            val = data[i][2]
            self.chaos[key] = val
        self.vin = 0
        self.vout = 0
        self.vbias = Vbias
        for i in range(100):
            if i == 0:
                self.vin = Vseed
            key = tuple((self.vbias, self.vin))
            self.vout = self.chaos[key]
        # TODO --> Assumes 3-bit capacitance variation of Cmem
        self.num_out = int(round((self.vout / 1.2) * 8))

    def step(self):
        # Use linear interpolation (preserving up to 1e-3 accuracy)
        self.vin = self.vout
        in1 = np.ceil(self.vin * 1000) / 1000
        in2 = np.floor(self.vin * 1000) / 1000
        key1 = tuple((self.vbias, in1))
        key2 = tuple((self.vbias, in2))
        out1 = self.chaos[key1]
        out2 = self.chaos[key2]
        self.vout = ((out1 - out2) * (self.vin - in2) / (in1 - in2)) + out2
        # TODO --> Assumes 3-bit capacitance variation of Cmem
        self.num_out = int(round((self.vout / 1.2) * 8))

    def get_vout(self):
        return self.vout

    def get_num_out(self):
        return self.vout
