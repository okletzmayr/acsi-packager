import unittest
from src.utils import fix_track_length


class TestTrackLengthFix(unittest.TestCase):
    # tests each case with
    # - a short track (1000m)
    # - a medium track (5500m)
    # - the famous Nordschleife (25378m)

    def test_km_short(self):
        self.assertEqual(fix_track_length('1.0km'), 1000)
        self.assertEqual(fix_track_length('1,0km'), 1000)
        self.assertEqual(fix_track_length('1km'), 1000)

    def test_km_middle(self):
        self.assertEqual(fix_track_length('5.5km'), 5500)
        self.assertEqual(fix_track_length('5,5km'), 5500)
        self.assertEqual(fix_track_length('5km'), 5000)

    def test_km_long(self):
        self.assertEqual(fix_track_length('25.378km'), 25378)
        self.assertEqual(fix_track_length('25,378km'), 25378)
        self.assertEqual(fix_track_length('25km'), 25000)

    def test_m_short(self):
        self.assertEqual(fix_track_length('1.000m'), 1000)
        self.assertEqual(fix_track_length('1,000m'), 1000)
        self.assertEqual(fix_track_length('1000m'), 1000)

    def test_m_middle(self):
        self.assertEqual(fix_track_length('5.500m'), 5500)
        self.assertEqual(fix_track_length('5,500m'), 5500)
        self.assertEqual(fix_track_length('5500m'), 5500)

    def test_m_long(self):
        self.assertEqual(fix_track_length('25.378m'), 25378)
        self.assertEqual(fix_track_length('25,378m'), 25378)
        self.assertEqual(fix_track_length('25378m'), 25378)

    def test_unitless_km_short(self):
        self.assertEqual(fix_track_length('1.0'), 1000)
        self.assertEqual(fix_track_length('1,0'), 1000)
        self.assertEqual(fix_track_length('1'), 1000)

    def test_unitless_km_middle(self):
        self.assertEqual(fix_track_length('5.5'), 5500)
        self.assertEqual(fix_track_length('5,5'), 5500)
        self.assertEqual(fix_track_length('5'), 5000)

    def test_unitless_km_long(self):
        self.assertEqual(fix_track_length('25.378'), 25378)
        self.assertEqual(fix_track_length('25,378'), 25378)
        self.assertEqual(fix_track_length('25'), 25000)

    def test_unitless_m_short(self):
        self.assertEqual(fix_track_length('1.000'), 1000)
        self.assertEqual(fix_track_length('1,000'), 1000)
        self.assertEqual(fix_track_length('1000'), 1000)

    def test_unitless_m_middle(self):
        self.assertEqual(fix_track_length('5.500'), 5500)
        self.assertEqual(fix_track_length('5,500'), 5500)
        self.assertEqual(fix_track_length('5500'), 5500)

    def test_unitless_m_long(self):
        self.assertEqual(fix_track_length('25.378'), 25378)
        self.assertEqual(fix_track_length('25,378'), 25378)
        self.assertEqual(fix_track_length('25378'), 25378)


if __name__ == '__main__':
    unittest.main(verbosity=2)
