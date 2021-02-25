import unittest
import helper_functions as H

class TestHelperFunctions(unittest.TestCase):

    def test_addTPTStep_signalsPopulated(self):
        '''
            Testing function:
                addTPTStep(testObj, line, signals, missingSignals)
        '''
        signals = {}
        signals['sig1'] = 'aaa'
        signals['sig2'] = 'bbb'
        signals['sig3'] = 'ccc'
        signals['sig3 status'] = 'ccc status'
        signals['sig4'] = 'ddd'

        testObj = []

        missingSignals = []

        lines = [
                    "| 1. | Set signal value of `sig1` to 2 | - |",
                    "| 6. | Set signal value of `sig2` to -60 | - |",
                    "| 6. | Set signal status of `sig3` to 0 | - |",
                    "| 11. | Ramp `sig3` to 20 with 10/s.| - |",
                    "| 13. | Check value of `sig4` | `sig4` = `sig3`|",
                    "| 11. | Check value of `sig1` | `sig1` = 1 |",
                    "| 11. | Check value of `sig1` | `sig1` = `sig2` +/- 0.02 |",
                    "| 11. | Check value of `sig1` | `sig1` = 20 +/- 0.02 |",
                    "| 9. | Run component until `sig1` = 60 | - |",
                    "| 10. | Run component for 100 ms | - |",
                    "| 10. | Run the component in cyclic run mode | - |",
                    "| >> | >>>> Comment text <<<< | << |"
        ]

        expected_outputs = [
                                ["Set aaa to 2.0"],
                                ["Set bbb to -60.0"],
                                ["Set ccc status to 0.0"],
                                ["Ramp ccc to 20.0 with 10.0/s"],
                                ["Compare ddd == ccc"],
                                ["Compare aaa == 1.0"],
                                ["Compare aaa == bbb +/- 0.02"],
                                ["Compare aaa == 20.0 +/- 0.02"],
                                ["Wait until aaa == 60.0"],
                                ["Wait 100.0ms"],
                                ["Wait 40ms"],
                                ["//  >>>> Comment text <<<< "]
        ]


        for line, expected_output in zip(lines, expected_outputs):
            testObj = []
            H.addTPTStep(testObj, line, signals, missingSignals)
            print(f"line = {line}")
            print(f"expected_output = {expected_output}")
            print(f"actual_output = {testObj}\n")
            self.assertEqual(testObj, expected_output)



    def test_addTPTStep_noSignals(self):

        signals = {}

        testObj = []

        lines = [
                    "| 1. | Set signal value of `sig1` to 2 | - |",
                    "| 6. | Set signal value of `sig2` to -60 | - |",
                    "| 11. | Ramp `sig3` to 20 with 10/s.| - |",
                    "| 13. | Check value of `sig4` | `sig4` = `sig3`|",
        ]

        expected_outputs = [
                                ["sig1"],
                                ["sig2"],
                                ["sig3"],
                                ["sig4"]
        ]


        for line, expected_output in zip(lines, expected_outputs):
            missingSignals = []
            H.addTPTStep(testObj, line, signals, missingSignals)
            print(f"line = {line}")
            print(f"expected_output = {expected_output}")
            print(f"actual_output = {missingSignals}\n")
            self.assertEqual(missingSignals, expected_output)


if __name__ == '__main__':
    unittest.main()