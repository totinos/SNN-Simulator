# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 14:51:04 2018

@author: madnan
"""

import numpy as np
import matplotlib.pyplot as plt


n = 2250

HRS = 16e3
LRS = 9e3
tswp = 100e-9
tswn = 100e-9
Vthp = 0.75
Vthn = 0.75

delT = 10e-9
Vt = 1.2

Gm = 1/LRS - 1/HRS

STDP_cycle = 1

#Gmax = np.ones(n) * Gm

# neuron parameters
tper = 10e-9
#cap = 10e-12
vthn = 0.00001


cap = 2.9166e-13
# MODIFYING THE CAP VALUES TO REFLECT THE NEURON IN CADENCE
#cap = 745e-15
#cap_base_value = 745e-15
#cap_values = [50e-15, 80e-15, 100e-15]
#print(cap_values)


Mp_in = 11929.23834
Mn_in = 12500


#Statistical parameters of Memristors
mu_hrs,sigma_hrs = HRS,HRS*0.2
mu_lrs,sigma_lrs = LRS,LRS*0.1
mu_vtn,sigma_vtn = 0.75,0.75*0.1
mu_vtp,sigma_vtp = 1,1*0.1
mu_tswn,sigma_tswn = 1e-6,1e-6*0.05
mu_tswp,sigma_tswp = 10e-9,10e-9*0.05


# Memristor Model  
M_dec = (HRS-LRS)*(delT/tswp)*(Vt/Vthp)
M_inc = (HRS-LRS)*(delT/tswn)*(Vt/Vthn)

##########################################################
#                                                        #
#  Definition of Neuron Class                            #
#  Neuron Membrane potential and firing events are       #
#  initialized as empty arrays while threshold and       # 
#  refractory period is assigned from the network file.  #0
#  Each neuron is also assigned a name given in network. #
#  Synapses connected to the input of the neuron are also#
#  listed.                                               #
#                                                        #
########################################################## 

class Neuron:
    def __init__(self, vmem=0, fire=0, vth=0, rf=0, Name=''):
        self.vmem = np.zeros(n)
        self.fire = np.zeros(n)

        # Define the starting capacitance of integrator
        #self.cap = cap
        self.vth = vth - 1
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
        self.Mp = np.ones(n) * Mp
        self.Mn = np.ones(n) * Mn
        G = 1/Mp - 1/Mn
        self.G = np.ones(n) * G
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
        self.G = np.ones(n) * G
        self.d = d
        self.N1 = N1
        
    def __str__(self):
        return 'Geff = ' + str(self.G/Gm) + ' Connection ' + self.N1.Name

##########################################################
#                                                        #
#  Reading input file to determine the number of clock   #
#  cycles and input spiking events                       #
#                                                        #
########################################################## 


textfile_in = open("file.txt", "r")
linecount = 1
inNeu_list=[]
inSyn_list=[]

for line in textfile_in:
    line = line.split() # to deal with blank 
    if line:            # lines (ie skip them)
        line = [float(i) for i in line]
        #inp.append(line)
        inNeu_list.append(inNeu(line,'inNI'+str(linecount).zfill(2)))
        inSyn_list.append(inSyn(Mp_in,Mn_in,0,inNeu_list[linecount-1]))
        linecount += 1

n= len(line)
    
textfile_in.close()


##########################################################
#                                                        #
#  Reads neurons and synapses from network file and      #
#  stores them in local memory                           #
#                                                        #
##########################################################
textfile = open("smallnetdesc.txt", "r")
neuron_list = {}
synapse_list = []
input_neuron_count = 0
neuron_count = 0
synapse_count = 0

for line in textfile:
    if line[:1] == 'N':
        # Vmem fire vth refr name
        temp_line = line.rsplit(" ")
        neuron_list[temp_line[1]] = Neuron(0, 0,  float(temp_line[2]), int(temp_line[3][:-1]), temp_line[1])
        if temp_line[1][0] == 'I':
            input_neuron_count += 1
        neuron_count += 1
        
    if line[:1] == 'S':
        temp_line = line.rsplit(" ")
        # Mp Mn delay N1 N2
        temp = Synapse(float(temp_line[5][:-1])*1e3, float(temp_line[6][:-1])*1e3, int(temp_line[4][:-1]), neuron_list[temp_line[1]], neuron_list[temp_line[2]])
        synapse_list.append(temp)
        synapse_count += 1
        
    if line[:1] == '#':
        # so it will stop at the beginning of the next network
        break

textfile.close()


##########################################################
#                                                        #
#  Find the input synapses connected to the input        #
#  neurons                                               #
#                                                        #
##########################################################

count = 0
for x in neuron_list:
    if x[0] == 'I':   
        neuron_list[x].input_connections.append(inSyn_list[count])
        count += 1


##########################################################
#                                                        #
#  Find all other synapses connected to the inputs of    #
#  each neuron in the network and set up connections     #
#                                                        #
##########################################################
for ne in neuron_list:
    for s in synapse_list:
        if neuron_list[ne].Name == s.N2.Name:
            neuron_list[ne].input_connections.append(s)


##########################################################
#                                                        #
#  DEBUGGING - Print out neurons and synapses for tests  #
#                                                        #
##########################################################
#for ne in neuron_list:
#    print(ne)
#    for s in neuron_list[ne].input_connections:
#        print(s)
#    print()
#
#for s in synapse_list:
#    print(s)


##########################################################
#                                                        #
#  Run discrete simulation, advancing clock iteratively  #
#                                                        #
##########################################################
for clk in range(n-1):
    for ne in neuron_list:
        neuron_list[ne].accum(clk, neuron_list[ne].input_connections)
    for s in synapse_list:
        s.STDP(clk)


##########################################################
#                                                        #
#  DEBUGGING - Print out neurons and synapses after run  #
#                                                        #
##########################################################
#for ne in neuron_list:
#    print(ne)
#    for s in neuron_list[ne].input_connections:
#        print(s)
#    print()
#
#for s in synapse_list:
#    print(s)

##########################################################
#                                                        #
#  Print out the resulting fires from all neurons        #
#                                                        #
##########################################################
        
#for ne in neuron_list:
#    print(neuron_list[ne])
        
print_startCLK=0
print_endCLK=100

plt.close("all")

plt.figure(1)

plt.subplot(711)
plt.plot(neuron_list['I01'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(712)
plt.plot(neuron_list['I02'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(713)
plt.plot(neuron_list['I03'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(714)
plt.plot(neuron_list['I04'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(715)
plt.plot(neuron_list['I05'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(716)
plt.plot(neuron_list['I06'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(717)
plt.plot(neuron_list['I07'].fire[print_startCLK:print_endCLK])
plt.show()






plt.figure(2)

plt.subplot(711)
plt.plot(inNeu_list[0].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(712)
plt.plot(inNeu_list[1].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(713)
plt.plot(inNeu_list[2].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(714)
plt.plot(inNeu_list[3].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(715)
plt.plot(inNeu_list[4].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(716)
plt.plot(inNeu_list[5].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(717)
plt.plot(inNeu_list[6].fire[print_startCLK:print_endCLK])
plt.show()



plt.figure(3)
plt.subplot(311)
plt.plot(neuron_list['O01'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(312)
plt.plot(neuron_list['O02'].fire[print_startCLK:print_endCLK])
plt.show()

plt.subplot(313)
plt.plot(neuron_list['O03'].fire[print_startCLK:print_endCLK])
plt.show()

output1=neuron_list['O01'].fire
output2=neuron_list['O02'].fire
output3=neuron_list['O03'].fire

sz = len(output1)

listOut=[]

for i in range(150):

    c1=sum(output1[i*15:(i+1)*15])
    c2=sum(output2[i*15:(i+1)*15])
    c3=sum(output3[i*15:(i+1)*15])
    if (c3 > c1 and c3 > c2):
        listOut.append("Iris-virginica")
    elif (c2 > c1 and c2 > c3):
        listOut.append("Iris-versicolor")
    elif (c1 > c2 and c1 > c3):
        listOut.append("Iris-setosa")
    elif (c1 == c2 and c1>c3):
        listOut.append("Iris-setosa")
    elif (c2 == c3 and c2>c1):
        listOut.append("Iris-versicolor")
    elif (c1==c3 and c1>c3):
        listOut.append("Iris-setosa")
    else:
        listOut.append("Iris-setosa")
#    print(i, end=' ')
#    print(listOut[-1])
  
infile="labels_out.txt"
      
textfile_in = open(infile, "r")

listLabel=[]


for line in textfile_in:
    a=line[64:-1]
    listLabel.append(a)
#    print(a)
   
textfile_in.close()

c=[]
count = 0
acc=[]

wrongI =[]

for i in range(150):
    count += listOut[i] == listLabel[i]
    acc.append(count*100/(i+1))
    c.append(listOut[i] == listLabel[i])
    if (listOut[i] != listLabel[i]):
        wrongI.append(i+1)
    
        
plt.figure(4)

plt.subplot(211)
plt.plot(c)
plt.show()
print(sum(c))
        
plt.subplot(212)
plt.plot(acc)
plt.show()

print(acc[-1])
print(wrongI)
