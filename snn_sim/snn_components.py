import math

# Import parameters from params.py (must import before numpy
# because there is a list with the name np in params.py)
from params import *
import numpy as np

# chaos=True


##########################################################
#                                                        #
#  Definition of Neuron Class                            #
#  Neuron Membrane potential and firing events are       #
#  initialized as empty arrays while threshold and       # 
#  refractory period is assigned from the network file.  #
#  Each neuron is also assigned a name given in network. #
#  Synapses connected to the input of the neuron are also#
#  listed.                                               #
#                                                        #
########################################################## 


class Chaos_RNG:
    def __init__(self, lookup_table, Vseed, Vbias):

        # Get data from lookup table (TAKES TIME)
        data = np.genfromtxt(lookup_table)

        # Place the contents of the table in a dict
        self.chaos = {}
        for i in range(len(data)):
            key = tuple((data[i][0], data[i][1]))
            val = data[i][2]
            self.chaos[key] = val

        # Set up internal variables
        self.vin = 0
        self.vout = 0
        self.vbias = Vbias

        # Initialize the RNG by running through some combinations
        for i in range(100):
            if i == 0:
                self.vin = Vseed
            key = tuple((self.vbias, self.vin))
            self.vout = self.chaos[key]
        
        # Set up output for easy bit split
        self.num_out = int(round((self.vout / 1.2) * 8))
    
    def step(self):
        
        self.vin = self.vout
        
        # Round LUT output values to nearest LUT input value
        # self.vin = round(self.vin * 400) / 400
        # key = tuple((self.vin, self.vbias))
        # self.vout = self.chaos[key]

        # Use linear interpolation (preserving all decimals)
        # in1 = np.ceil(self.vin * 400) / 400
        # in2 = np.floor(self.vin * 400) / 400
        in1 = np.ceil(self.vin * 1000) / 1000
        in2 = np.floor(self.vin * 1000) / 1000
        key1 = tuple((self.vbias, in1))
        key2 = tuple((self.vbias, in2))
        out1 = self.chaos[key1]
        out2 = self.chaos[key2]
        self.vout = ((out1 - out2) * (self.vin - in2) / (in1 - in2)) + out2
        # print("Vin:", self.vin)
        # print(in1)
        # print(in2)
        # print("Prop:",(self.vin-in2)/(in1-in2))
        # print("Times:",out1-out2)
        # print("Vout:", self.vout)
        # print(out1)
        # print(out2)
        # print("----------")

        self.num_out = int(round((self.vout / 1.2) * 8))
    
    def get_vout(self):
        return self.vout

    def get_num_out(self):
        return self.num_out


class Std_RNG:
    def __init__(self):
        self.num_out = 0

    def step(self):
        self.num_out = np.random.randint(8)

    def get_num_out(self):
        return self.num_out



################## HOW DOES DELAY WORK IN THE FRAMEWORK? --> Does the delay
# happen before the memristive part of the synapse, or does it happen after?
# Can there be more than one spike in a synapse at any given time?

class Neuron:
    def __init__(self, name="N0", vmem=Vrst, vth=0, rf=0, cap=cap, stochastic=False, rng=Std_RNG()):
        
        self.name = name
        self.Vth = Vrst - vth * Vdiff

        # Set refractory to 0 when not in ref period,
        # If you are in refractory period, then this
        # variable holds the number of cycles that
        # remain in the ref period
        self.refractory = rf
        self.refractory_cycles_left = 0

        # Holds a list of synapses that are connected at the input of the neuron
        self.in_syn_list = []

        # Create lists to store vmem values and neuron activity
        # self.Vmem = [vmem]*cycles
        self.Vmem = np.ones(cycles) * vmem
        # self.fire = [0]*cycles
        self.fire = np.zeros(cycles)
        # self.power_stages = np.zeros(cycles, dtype='|S1')
        self.power_stages = [0]*cycles

        self.stochastic = stochastic


        if self.stochastic == True:
            self.cap = cap + 2e-12
            self.cap_mask = 0
            self.c1_mask = 1 # Binary 0b0001
            self.c2_mask = 3 # Binary 0b0010
            self.c3_mask = 5 # Binary 0b0100
            self.rng = rng
        else:
            self.cap = cap



    def accum(self, clk):

        # TODO --> This function heavily depends on each consecutive call of accum
        #          being for the next consecutive clock cycle, probably won't work otherwise

        # if (clk == 5 or clk == 6 or clk == 7) and self.name == 'O0':
        # if self.name == 'O0':
        #             print("ACCUM FOR CLK CYCLE {}".format(clk))

        # If the neuron is in the refractory period, the neuron cannot accumulate
        # Vmem should always be at reset voltage when in refractory period
        # Does not account for leakage current
        #      Does leakage current matter when Vmem is at Vrst level?
        if self.refractory_cycles_left > 0:
            self.refractory_cycles_left -= 1

            # If the neuron is not firing this cycle, it is idle
            if self.fire[clk+1] == 1:
                self.power_stages[clk] = 'F'
            else:
                self.power_stages[clk] = 'I'
            # self.power_stages[clk] = 'R'

            return

        # Loop through the connected synapses to accumulate charge
        for synapse in self.in_syn_list:

            # Check to see if the neuron can accumulate charge
            if synapse.activity[clk] != 0:

                # The neuron is accumulating
                self.power_stages[clk] = 'A'

                # Essentially delta_t*current/C = delta_v
                delta_Vmem = tper * synapse.activity[clk] / self.cap
                self.Vmem[clk] -= delta_Vmem

                # if (clk == 5 or clk == 6 or clk == 7) and self.name == 'O0':
                # if self.name == 'O0':
                #     print("CHECKING VMEM ACCUMULATION --> CLK: {}".format(clk))
                #     print("    {} -> {}".format(synapse.pre.name, synapse.post.name))
                #     print("    synapse G:  {}".format(synapse.G[clk]))
                #     print("    syn activ:  {}".format(synapse.activity[clk]))
                #     print("    delta_Vmem: {}".format(delta_Vmem))
                #     print("    Vmem:       {}".format(self.Vmem[clk]))

                # Boundary condition when Vmem hits a rail
                if self.Vmem[clk] < VSS:
                    self.Vmem[clk] = VSS
                if self.Vmem[clk] > VDD:
                    self.Vmem[clk] = VDD

                # Check to see if the neuron should fire
                # If so, reset Vmem and enter refractory period, no need to accumulate further
                # TODO --> Is returning like this an optimization? (AKA should I keep it)
                if self.Vmem[clk] < self.Vth:
                    self.fire[clk+2] = 1
                    self.Vmem[clk+1] = Vrst
                    self.refractory_cycles_left = self.refractory

                    if self.stochastic == True:
                        # Get the new capacitance value to use
                        # cap_bits = np.random.randint(8)
                        cap_bits = self.rng.get_num_out()

                        # Reset capacitance to default value
                        self.cap = cap

                        # Add the other capacitances if the corresponding bits are 1
                        if (cap_bits & self.c1_mask) == self.c1_mask:
                            self.cap += c1
                        if (cap_bits & self.c2_mask) == self.c2_mask:
                            self.cap += c2
                        if (cap_bits & self.c3_mask) == self.c3_mask:
                            self.cap += c3

                        # print(self.cap)

                    return

            # TODO --> Should anything happen here?
            else:
                # The neuron is idle
                if self.power_stages[clk] == 0:
                    self.power_stages[clk] = 'I'

        # TODO --> Implement leakage current calculation here?
        # Copy the Vmem for this clock cycle to the vmem for the next cycle
        self.Vmem[clk+1] = self.Vmem[clk]

        return


##########################################################
#                                                        #
#  Definition of Synapse Class                           #
#  Memristor Mp, Mn and synaptic delay is assigned from  #
#  network file. Pre-Neuron, N1 and post neuron, N2      #
#  connections are also assigned.                        #
#                                                        #
##########################################################
class Synapse:
    def __init__(self, Mp=25e3, Mn=25e3, delay=0, pre=None, post=None):
        
        # Gangotree's definition of "delay" is 2 clock cycles
        self.delay = [0]*(delay * clk_per_del)

        # self.activity = [0]*cycles
        self.activity = np.zeros(cycles)
        
        # OTHER PARAMETERS
        self.pre = pre
        self.post = post

        self.Gmax = 1/LRS - 1/HRS
        self.G = np.ones(cycles) * (1/Mp - 1/Mn)

        self.power_stages = [0]*cycles

        #######################
        # FROM THE OLD SYNAPSE
        #######################
        # self.Mp = np.ones(cycles) * Mp
        # self.Mn = np.ones(cycles) * Mn
        # G = 1/Mp - 1/Mn
        # self.Gm = 1/LRS - 1/HRS
        # self.G = np.ones(cycles) * G
        # self.Memp = Memristor('Mp_'+ self.N1.Name + '-->' + self.N2.Name)
        # self.Memn = Memristor('Mn_'+ self.N1.Name + '-->' + self.N2.Name)


    def shift_spikes(self, clk):

        # Find length of delay line and magnitude of output current
        delay_len = len(self.delay)
        # current = Vr2r * self.G[clk]
        current = Vdiff * self.G[clk]

        # If delay == 0, there's no need to shift through the delay line
        if delay_len > 0:

            # TODO --> Determine if this should be [clk] or [clk+1]
            self.activity[clk] = self.delay[delay_len-1] * current
            for i in reversed(range(1, delay_len)):
                # print(i-1)
                self.delay[i] = self.delay[i-1]
            # Move the fire of the pre-neuron into the delay line
            self.delay[0] = self.pre.fire[clk]
        else:
            # Copy the fire of the pre-neuron directly into the synapse activity array
            # TODO --> check that the clock cycle here is correct
            # self.activity[clk+1] = self.pre.fire
            self.activity[clk] = self.pre.fire[clk] * current
            # pass

        # Determine whether the synapse is idle or active
        if self.activity[clk] != 0:
            self.power_stages[clk] = 'I'
        else:
            self.power_stages[clk] = 'A'


##########################################################
#                                                        #
#  Definition of pseudo input neuron Class               #
#  Provides input to the input synapses of real input    #
#  neurons                                               #
#                                                        #
##########################################################
class InputNeuron:
    def __init__(self, fire, name):
        self.fire = fire
        self.name = name

# class InputSynapse:
#     def __init__(self, Mp=25e3, Mn=25e3, delay=0, pre=None, post=None):
#         self.Mp = Mp
#         self.Mn = Mn
#         G = 1/Mp - 1/Mn
#         self.G = np.ones(cycles) * G
#         self.delay = delay
#         self.pre = pre
#         self.post = post
#         self.activity = np.zeros(cycles)

#     def shift_spikes(self, clk):
#         self.activity[clk] = self.pre.fire[clk] * (Vr2r * self.G[clk])







##########################################################
#                                                        #
#  Definition of Memristor Class                         #
#  Initializes the memristive device with process        #
#  variation parameters.                                 # 
#  Also models the change in memristance                 #
#                                                        #
##########################################################
        
    
class Memristor:
    def __init__(self,Name):

        # TODO --> Fix these to the default parameters

        # self.HRS = np.random.normal(mu_hrs, sigma_hrs)
        # self.LRS = np.random.normal(mu_lrs, sigma_lrs)
        # self.VtN = np.random.normal(mu_vtn, sigma_vtn)
        # self.VtP = np.random.normal(mu_vtp, sigma_vtp)
        # self.tswN = np.random.normal(mu_tswn, sigma_tswn)
        # self.tswP = np.random.normal(mu_tswp, sigma_tswp)
        # self.Name = Name

        self.HRS = HRS
        self.LRS = LRS
        self.VtN = Vthn
        self.VtP = Vthp
        self.tswN = tswn
        self.tswP = tswp
        self.Name = Name
        
    def __str__(self):
        return self.Name + '\n HRS = ' + str(self.HRS/1000) +' k\u2126' \
                         + '\n LRS = ' + str(self.LRS/1000) +' k\u2126' \
                         + '\n VtN = ' + str(self.VtN)  +' V'\
                         + '\n VtP = ' + str(self.VtP)  +' V'\
                         + '\n tswN = ' + str(self.tswN*1e6)  +' \u03bcs'\
                         + '\n tswP = ' + str(self.tswP*1e9) +' ns'
    
    def Mdec(self):
        return (self.HRS-self.LRS)*(delT/self.tswP)*(Vt/self.VtP)
    
    def Minc(self):
        return (self.HRS-self.LRS)*(delT/self.tswN)*(Vt/self.VtN)










################################################################### FOR DEBUG ONLY (I think)
if __name__ == '__main__':
    pass
