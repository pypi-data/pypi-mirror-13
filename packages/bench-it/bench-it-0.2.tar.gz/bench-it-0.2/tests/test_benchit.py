from .context import *

import unittest
from benchit import BenchIt

class BenchItSuite(unittest.TestCase):

    def test_benchit(self):
        """
        Full benchmark test.
        Test starting, marking, stopping, and displaying the benchmark.
        """
        b = BenchIt()

        # Ensure start key is set on init
        self.assertEqual(len(b), 1)
        self.assertIn('_start', b.keys())

        # Set a marker
        b.mark('Unique Marker')
        self.assertIn('Unique Marker', b.keys())

        # Stop the benchmark
        b.stop()
        self.assertIn('_end', b.keys())

        # Ensure end time is after the start time
        self.assertGreater(b['_end'], b['_start'])

        # Check the output table
        with capture(b.display) as output:
            self.assertIn("Avg Time", output)
            self.assertIn("Unique Marker", output)
            self.assertIn("Total runtime", output)
            self.assertIn("test_benchit", output)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BenchItSuite))
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
