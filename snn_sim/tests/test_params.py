
import os
import json
import unittest

import params

class TestParamsMethods(unittest.TestCase):
    
    def test_setup(self):
        user_fn = "params/user_params.json"
        if os.path.exists(user_fn):
            os.remove(user_fn)
        
        user_params = {
            "Vrst": 0.6
        }

        params.setup(user_params)
        self.assertTrue(os.path.exists(user_fn))

        with open(user_fn) as f:
            data = json.load(f)
        
        self.assertEqual(user_params["Vrst"], data["Vrst"])
        
    
    def test_get(self):

        # If the needed file doesn't exist, create it using params.setup()
        user_fn = "params/user_params.json"
        if not os.path.exists(user_fn):
            params.setup()

        # Check return types of request for multiple parameters
        p1, p2, p3, p4, p5 = params.get("VDD", "VSS", "tper", "cycles", "cap")
        self.assertTrue(isinstance(p1, float))
        self.assertTrue(isinstance(p2, int))
        self.assertTrue(isinstance(p3, float))
        self.assertTrue(isinstance(p4, int))
        self.assertTrue(isinstance(p5, float))

        # Check return type of request for one parameter
        p6 = params.get("VDD")
        self.assertTrue(isinstance(p6, float))

if __name__ == "__main__":
    unittest.main()
