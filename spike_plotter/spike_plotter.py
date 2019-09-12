import matplotlib.pyplot as plt

# This is a new file

class SpikePlotter:
    
    def __init__(self):
        self.x = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
        self.y = [ 0, 0, 0, 1, 0, 1, 0, 1, 1, 0 ]

    def plot(self):
        plt.step(self.x, self.y, where=post)
        plt.show

sp = SpikePlotter()
sp.plot()
