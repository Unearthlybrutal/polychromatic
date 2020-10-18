#!/usr/bin/python3
#
# Working directory should be the repository root.
#

import unittest

# Test Modules
import _backends

# Initalise OpenRazer daemon's fake devices
OPENRAZER_DAEMON = _backends.OpenRazerTest()

# Polychromatic Modules
from pylib import common as common
from pylib import middleman as middleman

# Begin testing!
class OpenRazerMiddlemanTest(unittest.TestCase):
    """
    Test many OpenRazer devices against the middleman layer.
    """
    @classmethod
    def setUpClass(self):
        OPENRAZER_DAEMON.start_daemon()

        self.dbg = common.Debugging()

        def _dummy_i18n(string):
            return string

        self.middleman = middleman.Middleman(self.dbg, common, _dummy_i18n)
        self.middleman.init()

        # Do not download device images
        self.middleman.get_backend("openrazer").allow_image_download = False

    @classmethod
    def tearDownClass(self):
        OPENRAZER_DAEMON.stop_daemon()
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_backend_is_loaded(self):
        self.assertNotEqual(self.middleman.get_backend("openrazer"), None, "OpenRazer backend isn't loaded")

    def test_get_device_list(self):
        self.assertNotEqual(self.middleman.get_device_list(), [], "No devices returned")

    def test_get_keyboards(self):
        self.assertLess(len(self.middleman.get_filtered_device_list("keyboard")), len(self.middleman.get_device_list()), "Cannot filter keyboards from all devices")

    def test_get_device_all(self):
        success = True
        for item in self.middleman.get_device_list():
            device = self.middleman.get_device("openrazer", item["uid"])
            if device in [None, str]:
                print("Failed to get_device(): {0} (Got: {1})".format(item["name"], str(device)))
                success = False
        self.assertEqual(success, True, "Failed to get_device() on one (or more) devices")

    def test_set_effect_no_parameter(self):
        success = True
        for device in self.middleman.get_device_list():
            for zone in device["zones"]:
                result = self.middleman.set_device_state(device["backend"], device["uid"], device["serial"], zone, "static", None, ["#00FF00"])
                if result != True:
                    print("Failed to set_device_state() effect: {0} (Got: {1})".format(device["name"], str(result)))
                    success = False
        self.assertEqual(success, True, "Failed to set a basic effect on one (or more) devices")

    def test_set_effect_with_parameter(self):
        success = True
        for device in self.middleman.get_device_list():
            for zone in device["zones"]:
                result = self.middleman.set_device_state(device["backend"], device["uid"], device["serial"], zone, "wave", 1, [])
                if result != True:
                    print("Failed to set_device_state() effect: {0} (Got: {1})".format(device["name"], str(result)))
                    success = False
        self.assertEqual(success, True, "Failed to set a parameter effect on one (or more) devices")

    def test_set_effect_with_colours(self):
        success = True
        for device in self.middleman.get_device_list():
            for zone in device["zones"]:
                result = self.middleman.set_device_state(device["backend"], device["uid"], device["serial"], zone, "breath", "dual", ["#00FF00", "#FF0000"])
                if result != True:
                    print("Failed to set_device_state() effect: {0} (Got: {1})".format(device["name"], str(result)))
                    success = False
        self.assertEqual(success, True, "Failed to set a multicolour effect on one (or more) devices")

    def test_set_brightness(self):
        success = True
        for device in self.middleman.get_device_list():
            for zone in device["zones"]:
                result = self.middleman.set_device_state(device["backend"], device["uid"], device["serial"], zone, "brightness", 50, ["#00FF00"])
                if result != True:
                    print("Failed to set_device_state() brightness: {0} (Got: {1})".format(device["name"], str(result)))
                    success = False
        self.assertEqual(success, True, "Failed to set brightness on one (or more) devices")

    def test_keyboard_has_layout(self):
        success = True
        for device in self.middleman.get_device_all():
            if device["form_factor"]["id"] == "keyboard" and len(device["keyboard_layout"]) < 2:
                success = False
        self.assertEqual(success, True, "Keyboard(s) do not have a valid layout")

    def test_get_matrix_object(self):
        success = True
        for device in self.middleman.get_device_all():
            if device["matrix"]:
                fx = self.middleman.get_device_object(device["backend"], device["uid"])
        self.assertEqual(success, True, "Supported device(s) failed to initalize a matrix")

    # BUG: Some mice known to fail due to incorrectly reporting having a matrix
    #      https://github.com/openrazer/openrazer/issues/1252
    def test_set_matrix_object(self):
        self.skipTest("Known Bug: openrazer/openrazer#1252")
        success = True
        for device in self.middleman.get_device_all():
            if device["matrix"]:
                try:
                    fx = self.middleman.get_device_object(device["backend"], device["uid"])
                    fx.set(0, 0, 255, 255, 255)
                    fx.draw()
                except Exception as e:
                    print("\n" + device["name"])
                    print(common.get_exception_as_string(e))
                    success = False
        self.assertEqual(success, True, "Supported device(s) failed to draw a matrix")

if __name__ == '__main__':
    unittest.main()