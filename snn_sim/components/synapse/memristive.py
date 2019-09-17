from params import *

class Synapse:
    def __init__(self, Mp=LRS, Mn=HRS, delay=0, pre=None, post=None):
        self.Mp = Mp
        self.Mn = Mn
        self.delay = delay
        self.pre = pre
        self.post = post
        self.Gmax = 1/LRS - 1/HRS
        
        print("Synapse created!")
        print(LRS)
        print(HRS)
        print(cycles)
        print(clk_per_del)

        
