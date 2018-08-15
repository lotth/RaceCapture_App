#
# Race Capture App
#
# Copyright (C) 2014-2017 Autosport Labs
#
# This file is part of the Race Capture App
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with
# this code. If not, see <http://www.gnu.org/licenses/>.

import unittest
import time
from autosportlabs.racecapture.alerts.alertrules import AlertRule, AlertRuleCollection


class AlertRuleTest(unittest.TestCase):

    def test_activate_deactivate(self):
        ar = AlertRule(True, 100, 200, 0.1, 0.1)
        self.assertFalse(ar.should_activate(100))
        time.sleep(0.2)
        self.assertTrue(ar.should_activate(100))


        self.assertFalse(ar.should_activate(90))
        self.assertFalse(ar.should_deactivate(90))
        # should still be active

        # wait until the deactivate threhold is tripped
        time.sleep(0.2)
        self.assertFalse(ar.should_activate(90))
        self.assertTrue(ar.should_deactivate(90))

    def test_enabled_disabled(self):
        # Test activating a disabled rule
        ar = AlertRule(False, 100, 200, 0.1, 0.1)
        self.assertFalse(ar.should_activate(100))
        time.sleep(0.2)
        self.assertFalse(ar.should_activate(100))

        # Test disabling after it's been activated
        ar2 = AlertRule(True, 100, 200, 0.1, 0.1)
        self.assertFalse(ar2.should_activate(100))
        time.sleep(0.2)
        self.assertTrue(ar2.should_activate(100))
        ar2.enabled = False

    def test_within_threshold(self):
        ar = AlertRule(True, 100, 200, 1, 1)
        self.assertTrue(ar.is_within_threshold(100))
        self.assertTrue(ar.is_within_threshold(150))
        self.assertTrue(ar.is_within_threshold(200))

        self.assertFalse(ar.is_within_threshold(99))
        self.assertFalse(ar.is_within_threshold(201))

class AlertRuleCollectionTest(unittest.TestCase):

    def test_enabled(self):
        ar = AlertRule(True, 100, 200, 0.1, 0.1)
        arc = AlertRuleCollection("RPM", False, [ar])

        active, deactive = arc.check_rules(50)
        self.assertEqual(active, [])
        self.assertEqual(deactive, [])

        time.sleep(0.2)
        active, deactive = arc.check_rules(50)
        self.assertEqual(active, [])
        self.assertEqual(deactive, [])

        arc.enabled = True
        active, deactive = arc.check_rules(50)
        time.sleep(0.2)
        active, deactive = arc.check_rules(50)
        self.assertEqual(active, [])
        self.assertEqual(deactive[0], ar)

    def test_alert_single(self):
        ar = AlertRule(True, 100, 200, 0.1, 0.1)
        arc = AlertRuleCollection("RPM", True, [ar])

        active, deactive = arc.check_rules(50)
        self.assertEqual(active, [])
        self.assertEqual(deactive, [])

        time.sleep(0.2)

        active, deactive = arc.check_rules(50)
        self.assertEqual(active, [])
        self.assertEqual(deactive[0], ar)
        self.assertEqual(len(deactive), 1)

        active, deactive = arc.check_rules(150)
        self.assertEqual(active, [])
        self.assertEqual(deactive, [])

        time.sleep(0.2)

        active, deactive = arc.check_rules(150)
        self.assertEqual(active[0], ar)
        self.assertEqual(len(active), 1)
        self.assertEqual(deactive, [])

        time.sleep(0.2)

        active, deactive = arc.check_rules(250)
        self.assertEqual(active, [])
        self.assertEqual(deactive, [])

        time.sleep(0.2)

        active, deactive = arc.check_rules(250)
        self.assertEqual(active, [])
        self.assertEqual(deactive[0], ar)
        self.assertEqual(len(deactive), 1)

    def test_alert_multiple(self):
        ar1 = AlertRule(True, 100, 200, 0.1, 0.1)
        ar2 = AlertRule(True, 300, 400, 0.1, 0.1)
        ar3 = AlertRule(True, 500, 600, 0.1, 0.1)
        arc = AlertRuleCollection("RPM", True, [ar1, ar2, ar3])

        active, deactive = arc.check_rules(50)
        self.assertEqual(active, [])
        self.assertEqual(deactive, [])

        time.sleep(0.2)
        active, deactive = arc.check_rules(50)
        self.assertEqual(active, [])
        self.assertEqual(deactive[0], ar1)
        self.assertEqual(deactive[1], ar2)
        self.assertEqual(deactive[2], ar3)
        self.assertEqual(len(deactive), 3)

        active, deactive = arc.check_rules(100)
        self.assertEqual(active, [])
        self.assertEqual(deactive[0], ar2)
        self.assertEqual(deactive[1], ar3)
        self.assertEqual(len(deactive), 2)

        time.sleep(0.2)
        active, deactive = arc.check_rules(100)
        self.assertEqual(active[0], ar1)
        self.assertEqual(len(active), 1)
        self.assertEqual(deactive[0], ar2)
        self.assertEqual(deactive[1], ar3)
        self.assertEqual(len(deactive), 2)

        active, deactive = arc.check_rules(300)
        self.assertEqual(active, [])
        self.assertEqual(deactive[0], ar3)
        self.assertEqual(len(deactive), 1)

        time.sleep(0.2)
        active, deactive = arc.check_rules(300)
        self.assertEqual(active[0], ar2)
        self.assertEqual(len(active), 1)
        self.assertEqual(deactive[0], ar1)
        self.assertEqual(deactive[1], ar3)
        self.assertEqual(len(deactive), 2)


def main():
    unittest.main()

if __name__ == "__main__":
    main()
