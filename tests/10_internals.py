#!/usr/bin/python3
#
# Working directory should be the repository root.
#

import pylib.common as common
import pylib.controller as controller
import pylib.locales as locales
import pylib.preferences as preferences

import os
import unittest

class PolychromaticTests(unittest.TestCase):
    """
    Test the internals of Polychromatic.
    """
    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        self._ = locales.Locales("polychromatic-controller").init()
        self.dbg = common.Debugging()
        preferences.init(self._)

    def tearDown(self):
        pass

    def test_locales_can_be_set(self):
        i18n = locales.Locales("polychromatic-controller", "de_DE")
        _ = i18n.init()
        self.assertEqual(i18n._get_current_locale(), "de_DE", "Could not set up a German locale")

    def test_locales_can_translate_strings(self):
        _ = locales.Locales("polychromatic-controller", "de_DE").init()
        # EN: Breath | DE: Atem
        self.assertEqual(_("Breath"), "Atem", "Could not translate text in German")

    def test_locales_can_translate_colours(self):
        _ = locales.Locales("polychromatic-controller", "de_DE").init()
        if os.path.exists(preferences.path.colours):
            os.remove(preferences.path.colours)
        preferences.init(_)
        colours = preferences.load_file(preferences.path.colours)
        passed = False
        for item in colours:
            # EN: Green | DE: Grün
            if item["name"] == "Grün":
                passed = True
        self.assertTrue(passed, "Could not translate colour strings")

    def test_config_pref_read(self):
        data = preferences.load_file(preferences.path.preferences)
        self.assertFalse(data["controller"]["system_qt_theme"], "Could not init or read preferences file")

    def test_config_pref_write(self):
        newdata = preferences.load_file(preferences.path.preferences)
        newdata["controller"]["landing_tab"] = 2
        preferences.save_file(preferences.path.preferences, newdata)

        data = preferences.load_file(preferences.path.preferences)
        self.assertEqual(data["controller"]["landing_tab"], 2, "Could not write to preferences file")

    def test_config_pref_force_invalid_data(self):
        newdata = preferences.load_file(preferences.path.preferences)
        newdata["controller"]["system_qt_theme"] = 123456
        preferences.save_file(preferences.path.preferences, newdata)

        # load_file._validate() should correct this
        data = preferences.load_file(preferences.path.preferences)
        self.assertFalse(data["controller"]["system_qt_theme"], "Invalid data was not corrected")

    def test_data_path(self):
        self.assertTrue(common.get_data_dir_path().endswith("/data"))

    def test_get_form_factor(self):
        ff = common.get_form_factor(self._, "keyboard")
        self.assertEqual(list(ff.keys()), ["id", "icon", "label"], "Unexpected get_form_factor() output")

    def test_get_green_shades(self):
        shades = common.get_green_shades(self._)
        passed = True
        for shade in shades:
            if shade["hex"][1:3] != "00" or shade["hex"][5:7] != "00":
                passed = False
        self.assertTrue(passed, "Non-green hex values in get_green_shades()")

    def test_tray_icon_kde(self):
        os.environ["XDG_CURRENT_DESKTOP"] = "KDE"
        os.environ["GTK_THEME"] = "Breeze"
        self.assertEqual(common.get_default_tray_icon(), "img/tray/light/breeze.svg", "Could not detect KDE desktop for tray icon")
        del(os.environ["XDG_CURRENT_DESKTOP"])
        del(os.environ["GTK_THEME"])

    def test_tray_icon_ubuntu(self):
        self.assertEqual(common.get_default_tray_icon(), "img/tray/light/polychromatic.svg", "Coul not retrieve default tray icon")

    def test_get_icon(self):
        self.assertIsNotNone(common.get_icon("general", "controller"), "Could not retrieve an icon")

    def test_colour_bitmap(self):
        self.assertIsNotNone(common.generate_colour_bitmap(self.dbg, preferences.path, "#00FF00"), "Could not generate a bitmap")

    def test_rgb_to_hex(self):
        self.assertEqual(common.rgb_to_hex([0, 255, 0]), "#00FF00", "Could not convert RGB to hex")

    def test_hex_to_rgb(self):
        self.assertEqual(common.hex_to_rgb("#FF00FF"), [255, 0, 255], "Could not convert RGB to hex")

if __name__ == '__main__':
    unittest.main()