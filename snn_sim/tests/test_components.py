import unittest

from components.synapse import TwinMemristive as TM
from components.neuron import IntegrateAndFire as IAF
from components.neuron import InputNeuron as IN


class TestComponents(unittest.TestCase):
    

    def test_component_connectivity(self):
        input_array = [12345]
        
        # Create a simple network
        input_neuron = IN("I0", input_array)
        neuron = IAF("N0", Vmem=0.6, Vth=0.599, rf=1, cap=9e-12)
        synapse = TM(delay=0, pre=input_neuron, post=neuron)
        neuron.input_synapses.append(synapse)

        # Check network connectivity
        self.assertEqual(input_neuron, synapse.pre)
        self.assertEqual(neuron, synapse.post)
        self.assertEqual(synapse.pre.fire[0], input_array[0])
        self.assertEqual(synapse, neuron.input_synapses[0])


    def test_component_operation(self):
        
        # Example network input
        input_array = [ 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0 ]
        SIM_CYCLES = len(input_array)
		
        # Create a simple network
        input_neuron = IN("I0", input_array)
        neuron = IAF("N0", Vmem=0.6, Vth=0.599, rf=1, cap=9e-12)
        synapse = TM(delay=0, pre=input_neuron, post=neuron)
        neuron.input_synapses.append(synapse)

        # Run a simulation for the simple network
        for clk in range(SIM_CYCLES):
            synapse.propagate_spikes(clk)
            neuron.accumulate(clk)

        # Check simulation result
        self.assertEqual(neuron.fire[3], input_array[2])


    def test_component_reset(self):
        
        # Example network input
        input_array = [ 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0 ]
        SIM_CYCLES = len(input_array)
		
        # Create a simple network
        input_neuron = IN("I0", input_array)
        neuron = IAF("N0", Vmem=0.6, Vth=0.599, rf=1, cap=9e-12)
        synapse = TM(delay=0, pre=input_neuron, post=neuron)
        neuron.input_synapses.append(synapse)

        # Run a simulation for the simple network
        for clk in range(SIM_CYCLES):
            synapse.propagate_spikes(clk)
            neuron.accumulate(clk)

        # Check simulation result
        self.assertEqual(neuron.fire[3], input_array[2])

        # Reset neuron & synapse
        neuron.reset()
        synapse.reset()

        # Check network connectivity and state variables after reset
        self.assertEqual(synapse, neuron.input_synapses[0])
        self.assertEqual(input_neuron, synapse.pre)
        self.assertEqual(neuron, synapse.post)
        self.assertTrue(neuron.fire[3] == 0)
        self.assertTrue(synapse.activity[2] == 0)
        

    def test_component_operation_after_reset(self):

        # Example network input
        input_array = [ 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0 ]
        SIM_CYCLES = len(input_array)
		
        # Create a simple network
        input_neuron = IN("I0", input_array)
        neuron = IAF("N0", Vmem=0.6, Vth=0.599, rf=1, cap=9e-12)
        synapse = TM(delay=0, pre=input_neuron, post=neuron)
        neuron.input_synapses.append(synapse)

        # Run a simulation for the simple network
        for clk in range(SIM_CYCLES):
            synapse.propagate_spikes(clk)
            neuron.accumulate(clk)
        
        # Check simulation result
        self.assertEqual(neuron.fire[3], input_array[2])

        # Reset the neuron & synapse and change synapse delay
        synapse.delay = 4
        neuron.reset()
        synapse.reset()

        # Run a new simulation
        for clk in range(SIM_CYCLES):
            synapse.propagate_spikes(clk)
            neuron.accumulate(clk)

        # Check new simulation result
        self.assertEqual(neuron.fire[7], input_array[2])


if __name__ == "__main__":
    unittest.main()
