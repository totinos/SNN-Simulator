import numpy as np
import matplotlib.pyplot as plt

# This is a new file

class SpikePlotter:
    
    def __init__(self):
        self.x = None
        self.y = None

    def plot(self, *args):

        max_len = 0
        num_waveforms = len(args)
        waveforms = []

        for arg in args:
            if not isinstance(arg, list):
                print("ERROR OCCURRED DURING PLOTTING")
                return 
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

if __name__ == "__main__":
    
    # Example waveforms with shape recognition signals
    v = [ 0, 0, 0, 1, 0, 0, 0, 0, 0 ]
    w = [ 0, 0, 1, 0, 1, 0, 0, 0, 0 ]
    x = [ 0, 0, 1, 0, 1, 0, 0, 0, 0 ]
    y = [ 0, 1, 0, 0, 0, 1, 0, 0, 0 ]
    z = [ 0, 1, 1, 1, 1, 1, 0, 0, 0 ]
    o = [ 0, 0, 0, 0, 0, 0, 0, 1, 0 ]

    sp = SpikePlotter()
    sp.plot(v, w, x, y, z, o)
