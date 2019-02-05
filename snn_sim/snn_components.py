

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
        self.vth = vth
        self.rf = rf
        self.Name = Name
        self.vmem[0] = vmem
        self.input_connections = []
        
    def accum1(self,clk,g):
        if 1.0 not in self.fire[max(0,clk+1-self.rf):clk+1]:
            self.vmem[clk:] = self.vmem[clk-1] - 0.6*g[clk-1]*tper/cap
            if self.vmem[clk] < self.vth:
                self.fire[clk+1] = 1
                self.vmem[clk+1:] = 0
                
    def accum(self,clk,S):
        if len(S) == 1:
            if S[0].N1.fire[max(0,clk-S[0].d)] == 1:
                self.accum1(clk,S[0].G)
        elif len(S) == 2:
            if S[0].N1.fire[max(0,clk-S[0].d)] == 1:
                self.accum1(clk,S[0].G)
            if S[1].N1.fire[max(0,clk-S[1].d)] == 1:
                self.accum1(clk,S[1].G)
                
    def __str__(self):
#        return self.Name +' Vmem = ' + str(self.vmem) + '\n' + 'Vf   = ' + str(self.fire)
        return self.Name + ' Vf = ' + str(self.fire)

class Neuron2:
    def __init__(self, nid=0, vmem=Vrst, cap=cap, vth=Vth, rf=0):
        self.id = nid
        self.vmem = np.zeros(cycles)
        self.vmem[0] = vmem
        self.fire = np.zeros(cycles)
        self.vth = vth
        self.rf = rf
        self.inputs = []
        self.outputs = []

    def accum(self, clk):
        pass




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
        
        self.HRS = np.random.normal(mu_hrs, sigma_hrs)
        self.LRS = np.random.normal(mu_lrs, sigma_lrs)
        self.VtN = np.random.normal(mu_vtn, sigma_vtn)
        self.VtP = np.random.normal(mu_vtp, sigma_vtp)
        self.tswN = np.random.normal(mu_tswn, sigma_tswn)
        self.tswP = np.random.normal(mu_tswp, sigma_tswp)
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
        self.G = np.ones(cycles) * G
        self.d = d
        self.N1 = N1
        self.N2 = N2
        self.Memp = Memristor('Mp_'+ self.N1.Name + '-->' + self.N2.Name)
        self.Memn = Memristor('Mn_'+ self.N1.Name + '-->' + self.N2.Name)
    

    def __str__(self):
        return 'Geff = ' + str(self.G/Gm) + ' Connection ' + self.N1.Name+ '-->' + self.N2.Name
    
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
