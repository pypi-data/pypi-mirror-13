import unittest
from warning import ExperimentWarning

class Warning_test(unittest.TestCase):
    
    def test_get_action(self):
        
        w = ExperimentWarning("name", "var1", 50.0, "gt", "immediately", "kill")
        self.assertEqual(w.get_action("war 50"), "no action")
        self.assertEqual(w.get_action("var1 nfasdjk"), "no action")
        self.assertEqual(w.get_action("var1 50"), "no action")
        self.assertEqual(w.get_action("var1 49"), "no action")
        self.assertEqual(w.get_action("var1 51"), "kill")
        
        w = ExperimentWarning("name", "var1", 35.0, "lt", "immediately", "kill")
        self.assertEqual(w.get_action("var1 35"), "no action")
        self.assertEqual(w.get_action("var1 34"), "kill")
        self.assertEqual(w.get_action("var1 36"), "no action")
        
        w = ExperimentWarning("name", "var1", 50.0, "geq", "immediately", "kill")
        self.assertEqual(w.get_action("var1 50"), "kill")
        self.assertEqual(w.get_action("var1 49"), "no action")
        self.assertEqual(w.get_action("var1 51"), "kill")
        
        w = ExperimentWarning("name", "var1", 50.0, "leq", "immediately", "warn")
        self.assertEqual(w.get_action("var1 50"), "warn")
        self.assertEqual(w.get_action("var1 49"), "warn")
        self.assertEqual(w.get_action("var1 51"), "no action")
        
        w = ExperimentWarning("name", "var1", 50.01, "eq", "immediately", "email")
        self.assertEqual(w.get_action("var1 50.01"), "email")
        self.assertEqual(w.get_action("var1 49"), "no action")
        self.assertEqual(w.get_action("var1 51"), "no action")
        
        w = ExperimentWarning("name", "var2", 50, "geq", "time 6000", "email")
        self.assertEqual(w.get_action("var2 50"), "no action")
        self.assertEqual(w.get_action("var2 49"), "no action")
        self.assertEqual(w.get_action("var2 51"), "no action")
        
        w = ExperimentWarning("name", "variable", 50, "geq", "time 0", "email")
        self.assertEqual(w.get_action("variable 50"), "email")
        self.assertEqual(w.get_action("variable 49"), "no action")
        self.assertEqual(w.get_action("variable 51"), "email")
        self.assertEqual(w.get_action("var1 51"), "no action")

if __name__ == '__main__':
    unittest.main()
