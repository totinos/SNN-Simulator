from snn_components import *

#################################################
#                                               #
#  NETWORK TO USE TO TEST                       #
#                                               #
#      1: IRIS                                  #
#      2: SHAPE RECOGNITION                     #
#                                               #
#################################################
network = 2


##########################################################
#                                                        #
#  Reading input file to determine the number of clock   #
#  cycles and input spiking events                       #
#                                                        #
##########################################################

if network == 1:
    textfile_in = open("../file.txt", "r")
else:
    textfile_in = open("../pwl_gen/out.txt", "r")

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

if network == 1:
    textfile = open("../smallnetdesc.txt", "r")
else:
    textfile = open("../shape_recog_net.txt", "r")

neuron_list = {}
synapse_list = []
input_neuron_count = 0
neuron_count = 0
synapse_count = 0

for line in textfile:
    # print(line)
    if line[:1] == 'N':
        # Vmem fire vth refr name
        temp_line = line.rsplit(" ")
        neuron_list[temp_line[1]] = Neuron(0, 0,  float(temp_line[2]), int(temp_line[3]), temp_line[1])
        if temp_line[1][0] == 'I':
            input_neuron_count += 1
        neuron_count += 1
        
    if line[:1] == 'S':
        temp_line = line.rsplit(" ")
        print(temp_line)
        # Mp Mn delay N1 N2
        temp = Synapse(float(temp_line[5])*1e3, float(temp_line[6])*1e3, int(temp_line[4]), neuron_list[temp_line[1]], neuron_list[temp_line[2]])
        synapse_list.append(temp)
        synapse_count += 1
        
    if line[:1] == '#':
        # so it will stop at the beginning of the next network
        break

textfile.close()
# print(neuron_list)
# print(synapse_list)


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


#################################################
#                                               #
#  IRIS                                         #
#                                               #
#################################################
if network == 1:

    output1=neuron_list['O01'].fire
    output2=neuron_list['O02'].fire
    output3=neuron_list['O03'].fire

    sz = len(output1)

    listOut=[]

    #----------------------------------

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

        # print(i, end=' ')
        # print(listOut[-1])


    infile="../labels_out.txt"
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

    print(acc[-1])
    print(wrongI)


#################################################
#                                               #
#  SHAPE RECOGNITION                            #
#                                               #
#################################################
else:

    output = neuron_list['O0'].fire

    np.set_printoptions(threshold=np.nan)
    print('Fires of I0')
    print(neuron_list['I0'].fire)
    print('Fires of H0')
    print(neuron_list['H0'].fire)
    # print(neuron_list['H0'])
    print('\nVmem of H0')
    print(neuron_list['H0'].vmem)
    print()
    print(synapse_list[0])
    print(neuron_list['H0'].vth)

    print()
    print(output)

    # Don't really know what this is for....
    # sz = len(output)
    # list_out = []
