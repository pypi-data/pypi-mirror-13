import gc
import os.path as osp
import time
import unittest
from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np

from pylinac.cbct import CBCT
from pylinac.core.geometry import Point
from tests.utils import save_file

VARIAN_DIR = osp.join(osp.dirname(__file__), 'test_files', 'CBCT', 'Varian')
ELEKTA_DIR = osp.join(osp.dirname(__file__), 'test_files', 'CBCT', 'Elekta')


class GeneralTests(TestCase):
    """Test general things when using cbct module."""

    def setUp(self):
        self.cbct = CBCT()

    def test_demo(self):
        """Run the demo to make sure it works."""
        self.cbct.run_demo()

    def test_helpers(self):
        """Test the various helper methods."""
        self.cbct.load_demo_images()
        self.cbct.analyze()
        self.cbct._return_results()

    def test_loading(self):
        """Test various loading schemes."""
        # load demo images
        CBCT.from_demo_images()

        # load from folder directly
        folder = osp.join(VARIAN_DIR, 'Pelvis')
        CBCT(folder)

        # load from zip file
        zfile = osp.join(VARIAN_DIR, 'CBCT_4.zip')
        CBCT.from_zip_file(zfile)

        # load from url
        CBCT.from_url('https://s3.amazonaws.com/assuranceqa-staging/uploads/imgs/CBCT_4.zip')

    def test_images_not_loaded(self):
        """Raise error if trying to analyze when images aren't loaded yet."""
        self.assertRaises(AttributeError, self.cbct.analyze)

    def test_bad_files(self):
        """Test bad file inputs."""
        not_a_folder = "notafolder"
        self.assertRaises(NotADirectoryError, self.cbct.load_folder, not_a_folder)

        not_a_zip = "notazip.zip"
        self.assertRaises(FileExistsError, self.cbct.load_zip_file, not_a_zip)

        not_image_folder = osp.join(osp.dirname(__file__), 'core')
        self.assertRaises(FileNotFoundError, self.cbct.load_folder, not_image_folder)

        no_CT_images_zip = osp.join(VARIAN_DIR, 'dummy.zip')
        self.assertRaises(FileNotFoundError, self.cbct.load_zip_file, no_CT_images_zip)

    @unittest.expectedFailure
    def test_images_not_from_same_study(self):
        """Loading images from different studies should raise and error."""
        mixed_zip = osp.join(VARIAN_DIR, 'mixed_studies.zip')
        with self.assertRaises(ValueError):
            self.cbct.load_zip_file(mixed_zip)

    def test_phan_center(self):
        """Test locations of the phantom center."""
        self.cbct.load_demo_images()

        known_phan_center = Point(257, 255)
        self.cbct.analyze()
        self.assertAlmostEqual(self.cbct.hu.phan_center.x, known_phan_center.x, delta=0.7)
        self.assertAlmostEqual(self.cbct.hu.phan_center.y, known_phan_center.y, delta=0.7)

    @unittest.skip
    def test_finding_HU_slice(self):
        """Test the robustness of the algorithm to find the HU linearity slice."""
        self.cbct.load_demo_images()

        self.assertEqual(self.cbct.settings.hu_slice_num, 32)

        # roll the phantom data by 4 slices
        np.roll(self.cbct.settings.images, 4, axis=2)

    def test_save_image(self):
        """Test that saving an image does something."""
        self.cbct.load_demo_images()
        self.cbct.analyze(hu_tolerance=10, scaling_tolerance=0.01)
        for method in ['save_analyzed_image', 'save_analyzed_subimage']:
            methodcall = getattr(self.cbct, method)
            save_file(methodcall)

    def test_plot_images(self):
        """Test the various plotting functions."""
        self.cbct.load_demo_images()
        self.cbct.analyze()

        self.cbct.plot_analyzed_image()
        for item in ['hu', 'un', 'mtf', 'sp', 'prof', 'lin', 'lc']:
            self.cbct.plot_analyzed_subimage(item)

        self.cbct.plot_analyzed_subimage('lin', delta=False)

        with self.assertRaises(ValueError):
            self.cbct.plot_analyzed_subimage('sr')


class CBCTMixin:
    """A mixin to use for testing Varian CBCT scans; does not inherit from TestCase as it would be run
        otherwise."""
    hu_tolerance = 40
    scaling_tolerance = 1
    zip = True
    expected_roll = 0
    slice_locations = {}
    hu_values = {}
    hu_passed = True
    unif_values = {}
    unif_passed = True
    mtf_values = {}
    avg_line_length = 50
    length_passed = True
    thickness_passed = True
    lowcon_visible = 0

    @classmethod
    def setUpClass(cls):
        if cls.zip:
            cls.cbct = CBCT.from_zip_file(cls.location)
        else:
            cls.cbct = CBCT(cls.location)
        cls.cbct.analyze(cls.hu_tolerance, cls.scaling_tolerance)

    @classmethod
    def tearDownClass(cls):
        delattr(cls, 'cbct')
        plt.close('all')
        time.sleep(1)
        gc.collect()

    def test_slice_thickness(self):
        """Test the slice thickness."""
        self.assertEqual(self.cbct.thickness.passed, self.thickness_passed)

    def test_lowcontrast_bubbles(self):
        """Test the number of low contrast bubbles visible."""
        self.assertAlmostEqual(self.cbct.lowcontrast.rois_visible, self.lowcon_visible, delta=1)

    def test_all_passed(self):
        """Test the pass flags for all tests."""
        self.assertEqual(self.cbct.hu.overall_passed, self.hu_passed)
        self.assertEqual(self.cbct.uniformity.overall_passed, self.unif_passed)
        self.assertEqual(self.cbct.geometry.overall_passed, self.length_passed)

    def test_slice_locations(self):
        """Test the locations of the slices of interest."""
        for attr, slice_name in zip(('hu_slice_num', 'un_slice_num', 'sr_slice_num', 'lc_slice_num'), ('HU', 'UN', 'SR', 'LC')):
            self.assertAlmostEqual(getattr(self.cbct.settings, attr), self.slice_locations[slice_name], delta=1)

    def test_phantom_roll(self):
        """Test the roll of the phantom."""
        self.assertAlmostEqual(self.cbct.settings.phantom_roll, self.expected_roll, delta=0.1)

    def test_HU_values(self):
        """Test HU values."""
        for key, roi in self.cbct.hu.rois.items():
            exp_val = self.hu_values[key]
            meas_val = roi.pixel_value
            self.assertAlmostEqual(exp_val, meas_val, delta=5)

    def test_uniformity_values(self):
        """Test Uniformity HU values."""
        for key, roi in self.cbct.uniformity.rois.items():
            exp_val = self.unif_values[key]
            meas_val = roi.pixel_value
            self.assertAlmostEqual(exp_val, meas_val, delta=5)

    def test_geometry_line_length(self):
        """Test the geometry distances."""
        self.assertAlmostEqual(self.avg_line_length, self.cbct.geometry.avg_line_length, delta=0.05)

    def test_MTF_values(self):
        """Test MTF values."""
        for key, exp_mtf in self.mtf_values.items():
            meas_mtf = self.cbct.spatialres.mtf(key)
            self.assertAlmostEqual(exp_mtf, meas_mtf, delta=0.1)


class CBCTDemo(CBCTMixin, TestCase):
    """Test the CBCT demo (Varian high quality head protocol)."""
    expected_roll = -0.3
    slice_locations = {'HU': 32, 'UN': 6, 'SR': 44, 'LC': 20}
    hu_values = {'Poly': -45, 'Acrylic': 117, 'Delrin': 341, 'Air': -998, 'Teflon': 997, 'PMP': -200, 'LDPE': -103}
    unif_values = {'Center': 17, 'Left': 10, 'Right': 0, 'Top': 6, 'Bottom': 6}
    mtf_values = {80: 0.76, 90: 0.61, 60: 0.99, 70: 0.88, 95: 0.45}
    avg_line_length = 49.92
    lowcon_visible = 3

    @classmethod
    def setUpClass(cls):
        cls.cbct = CBCT.from_demo_images()
        cls.cbct.analyze()


class CBCT4(CBCTMixin, TestCase):
    """A Varian CBCT dataset"""
    location = osp.join(VARIAN_DIR, 'CBCT_4.zip')
    expected_roll = -2.57
    slice_locations = {'HU': 31, 'UN': 6, 'SR': 43, 'LC': 19}
    hu_values = {'Poly': -33, 'Acrylic': 119, 'Delrin': 335, 'Air': -979, 'Teflon': 970, 'PMP': -185, 'LDPE': -94}
    unif_values = {'Center': 17, 'Left': 10, 'Right': 22, 'Top': 18, 'Bottom': 13}
    mtf_values = {80: 0.47, 90: 0.39, 60: 0.63, 70: 0.55, 95: 0.3}
    avg_line_length = 49.94
    # thickness_passed = False
    lowcon_visible = 3


class Elekta2(CBCTMixin, TestCase):
    """An Elekta CBCT dataset"""
    location = osp.join(ELEKTA_DIR, 'Elekta_2.zip')
    slice_locations = {'HU': 162, 'UN': 52, 'SR': 132, 'LC': 132}
    hu_values = {'Poly': -319, 'Acrylic': -224, 'Delrin': -91, 'Air': -863, 'Teflon': 253, 'PMP': -399, 'LDPE': -350}
    hu_passed = False
    unif_values = {'Center': -285, 'Left': -279, 'Right': -278, 'Top': -279, 'Bottom': -279}
    unif_passed = False
    mtf_values = {80: 0.53, 90: 0.44, 60: 0.74, 70: 0.63, 95: 0.36}
    avg_line_length = 49.22
    lowcon_visible = 2
