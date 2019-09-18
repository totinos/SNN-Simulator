import numpy as np

class RNG:
    def __init__(self):
        self.output = 0
    
    def step(self):
        self.output = np.random.randint(8)
    
    def get_output(self):
        return self.output
