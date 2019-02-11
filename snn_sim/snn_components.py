

# Import parameters from params.py (must import before numpy
# because there is a list with the name np in params.py)
from params import *
import numpy as np


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

class Neuron:
    def __init__(self, vmem=0, fire=0, vth=0, rf=0, Name=''):
        self.vmem = np.zeros(cycles)
        self.fire = np.zeros(cycles)

        # Define the starting capacitance of integrator
        #self.cap = cap

        # Set the threshold in volts
        self.vth = Vrst - vth * Vdiff
        print('Name:', Name, 'vth:', self.vth)
        # self.vth = vth

        self.rf = rf
        self.Name = Name
        self.vmem[0] = vmem
        self.input_connections = []
        
    def accum1(self,clk,g):
        if 1.0 not in self.fire[max(0,clk+1-self.rf):clk+1]:
            self.vmem[clk:] = self.vmem[clk-1] - Vdiff*g[clk-1]*tper/cap
            if self.vmem[clk] < self.vth:
                self.fire[clk+1] = 1
                self.vmem[clk+1:] = 0
                
    def accum(self,clk,S):
        
        # # Check all of the synapses connected at the input of the neuron
        # for i in range(len(S)):
            
        #     # Check if the pre-neuron for S[i] fired
        #     if S[i].N1.fire[max(0, clk-S[i].d)] == 1:
        #         self.accum1(clk, S[i].G)


        # PROVE THAT THIS OCCURS EVERY CLOCK CYCLE
        # if self.Name=='H0':
        #     print(clk)


        for i in range(len(S)):
            # self.vmem[clk] = 0
            if S[i].N1.fire[max(0, clk-S[i].d)] == 1:
                if 1.0 not in self.fire[max(0,clk+1-self.rf):clk+1]:
                    # if (self.vmem[clk] == self.vmem[clk-1]):
                    # self.vmem[clk:] = self.vmem[clk-1] - Vdiff*S[i].G[clk-1]*tper/cap
                    # else:
                    self.vmem[clk] -= Vdiff*S[i].G[clk-1]*tper/cap
                    self.vmem[clk+1:] = self.vmem[clk]
                    # self.vmem[clk:] = self.vmem[clk]
                    if self.vmem[clk] < self.vth:
                        self.fire[clk+1] = 1
                        self.vmem[clk+1:] = 0
            # if (self.Name == 'H0'):
            #     print('clk:', clk, self.vmem[clk])
            # # if (self.vmem[clk] != 0):
            # self.vmem[clk:] = self.vmem[clk-1] + self.vmem[clk]

                
    def __str__(self):
#        return self.Name +' Vmem = ' + str(self.vmem) + '\n' + 'Vf   = ' + str(self.fire)
        return self.Name + ' Vf = ' + str(self.fire)


################## HOW DOES DELAY WORK IN THE FRAMEWORK? --> Does the delay
# happen before the memristive part of the synapse, or does it happen after?
# Can there be more than one spike in a synapse at any given time?

class Neuron2:
    def __init__(self, name="N0", vmem=Vrst, vth=0, rf=0, cap=cap):
        
        self.name = name
        self.cap = cap
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
        self.Vmem = [vmem]*cycles
        self.fire = [0]*cycles


        # self.out_fire_buf = 0


    def accum(self, clk):

        for synapse in in_syn_list:

            # Check to see if the neuron can accumulate charge
            if synapse.activity[clk] and self.refractory_cycles_left == 0:

                # TODO --> Make this update correct
                # self.Vmem[clk] -= Vdiff*synapse.G[clk]

                # Check to see if the neuron can fire
                if self.Vmem[clk] < self.Vth:
                    self.fire[clk+1] = 1
                    self.Vmem[clk+1] = 0
                    self.refractory_cycles_left = self.refractory

            # Still in the refractory period, wait a cycle
            elif self.refractory_cycles_left > 0:
                self.refractory_cycles_left -= 1

            # TODO --> Think more about this and maybe implement it
            # Take into account leakage current????
            else:
                pass

        return

class Synapse2:
    def __init__(self, Mp=25e3, Mn=25e3, delay=0, pre=None, post=None):
        self.delay = [0]*delay
        self.activity = [0]*cycles
        # OTHER PARAMETERS
        self.pre = pre
        self.post = post

    def shift_spikes(self, clk):
        delay_len = len(self.delay)
        if delay_len > 0:

            # TODO --> Determine if this should be [clk] or [clk+1]
            self.activity[clk+1] = self.delay[delay_len-1]
            for i in reversed(range(1, delay_len)):
                print(i-1)
                self.delay[i] = self.delay[i-1]
            # Move the fire of the pre-neuron into the delay line
            self.delay[0] = self.pre.fire[clk]
        else:
            # Copy the fire of the pre-neuron directly into the synapse activity array
            # TODO --> check that the clock cycle here is correct
            # self.activity[clk+1] = self.pre.fire
            pass

class InputNeuron:
    def __init__(self, fire, name):
        self.fire = fire
        self.name = name

class InputSynapse:
    def __init__(self, Mp=25e3, Mn=25e3, delay=0, pre=None, post=None):
        self.Mp = Mp
        self.Mn = Mn
        G = 1/Mp - 1/Mn
        self.G = np.ones(cycles) * G
        self.delay = delay
        self.pre = pre
        self.post = post







##########################################################
#                                                        #
#  Definition of pseudo input neuron Class               #
#  Provides input to the input synapses of real input    #
#  neurons                                               #
#                                                        #
########################################################## 
    
class inNeu:
    def __init__(self, fire, Name):
        self.fire = fire
        self.Name = Name
        
    def __str__(self):
        return self.Name + ' Vf = ' + str(self.fire)


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


##########################################################
#                                                        #
#  Definition of Synapse Class                           #
#  Memristor Mp, Mn and synaptic delay is assigned from  #
#  network file. Pre-Neuron, N1 and post neuron, N2      # 
#  connections are also assigned.                        #
#                                                        #
########################################################## 

    
class Synapse:
    def __init__(self, Mp=25000, Mn=25000, d=0, N1=Neuron(0,0,0,0,'Vpre'), N2=Neuron(0,0,0,0,'Vpost')):
        self.Mp = np.ones(cycles) * Mp
        self.Mn = np.ones(cycles) * Mn
        G = 1/Mp - 1/Mn
        self.Gm = 1/LRS - 1/HRS
        self.G = np.ones(cycles) * G
        self.d = d
        self.N1 = N1
        self.N2 = N2
        self.Memp = Memristor('Mp_'+ self.N1.Name + '-->' + self.N2.Name)
        self.Memn = Memristor('Mn_'+ self.N1.Name + '-->' + self.N2.Name)
    

    def __str__(self):
        # return 'Geff = ' + str(self.G/self.Gm) + ' Connection ' + self.N1.Name+ '-->' + self.N2.Name
        return 'Geff = ' + str(self.G[0]) + ' Connection ' + self.N1.Name+ '-->' + self.N2.Name
    
    def LTP1(self,clk):
        self.Mp[clk] -= self.Memp.Mdec()
        self.Mn[clk] += self.Memn.Minc()
    
    def LTD1(self,clk):
        self.Mp[clk] += self.Memp.Minc()
        self.Mn[clk] -= self.Memn.Mdec()
    
#    def LTP1(self,clk):
#        self.Mp[clk] -= M_dec
#        self.Mn[clk] += M_inc
        
    def LTP2(self,clk):
        self.Mp[clk] -= 2*M_dec
        self.Mn[clk] += 2*M_inc    
    
    def LTP3(self,clk):
        self.Mp[clk] -= 3*M_dec
        self.Mn[clk] += 3*M_inc
        
    def LTP4(self,clk):
        self.Mp[clk] -= 4*M_dec
        self.Mn[clk] += 4*M_inc 
        
    def LTP5(self,clk):
        self.Mp[clk] -= 5*M_dec
        self.Mn[clk] += 5*M_inc
        
#    def LTD1(self,clk):
#        self.Mp[clk] += M_inc
#        self.Mn[clk] -= M_dec
        
    def LTD2(self,clk):
        self.Mp[clk] += 2*M_inc
        self.Mn[clk] -= 2*M_dec

    def LTD3(self,clk):
        self.Mp[clk] += 3*M_inc
        self.Mn[clk] -= 3*M_dec

    def LTD4(self,clk):
        self.Mp[clk] += 4*M_inc
        self.Mn[clk] -= 4*M_dec

    def LTD5(self,clk):
        self.Mp[clk] += 5*M_inc
        self.Mn[clk] -= 5*M_dec        
        
    def STDP(self,clk):
        self.Mp[clk] = self.Mp[clk-1]
        self.Mn[clk] = self.Mn[clk-1]
        
        if STDP_cycle == 1:
            if self.N1.fire[clk-self.d-1] == 1 and self.N2.fire[clk] == 1:
                self.LTP1(clk)
            elif self.N1.fire[clk-self.d] == 1 and self.N2.fire[clk] == 1:
                self.LTD1(clk)
        elif STDP_cycle == 2:
            if self.N1.fire[clk-self.d-2] == 1 and self.N2.fire[clk] == 1:
                self.LTP1(clk)
            elif self.N1.fire[clk-self.d-1] == 1 and self.N2.fire[clk] == 1:
                self.LTP2(clk)                
            elif self.N1.fire[clk-self.d] == 1 and self.N2.fire[clk] == 1:
                self.LTD2(clk)
            elif self.N1.fire[clk-self.d] == 1 and self.N2.fire[clk-1] == 1:
                self.LTD1(clk)
                
        if self.Mp[clk] < LRS:
            self.Mp[clk] = LRS
        if self.Mn[clk] < LRS:
            self.Mn[clk] = LRS
        if self.Mp[clk] > HRS:
            self.Mp[clk] = HRS
        if self.Mn[clk] > HRS:
            self.Mn[clk] = HRS

        self.G[clk] = 1/self.Mp[clk] - 1/self.Mn[clk]

##########################################################
#                                                        #
#  Definition of input Synapse Class                     #
#  Memristor Mp, Mn and synaptic delay is assigned from  #
#  network file. Also takes the input firing information # 
#                                                        #
########################################################## 

        
class inSyn:
    def __init__(self, Mp=LRS, Mn=HRS, d=0, N1=inNeu([],'')):
        self.Mp = Mp
        self.Mn = Mn
        G = 1/Mp - 1/Mn
        self.G = np.ones(cycles) * G
        self.d = d
        self.N1 = N1
        
    def __str__(self):
        return 'Geff = ' + str(self.G/Gm) + ' Connection ' + self.N1.Name



if __name__ == '__main__':
    pass
