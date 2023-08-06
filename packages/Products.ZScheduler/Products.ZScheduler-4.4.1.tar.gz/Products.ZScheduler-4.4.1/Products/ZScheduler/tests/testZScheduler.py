#
#    Copyright (C) 2011-2015  Corporation of Balclutha. All rights Reserved.
#
#    For your open source solution, bureau service and consultancy requirements,
#    visit us at http://www.balclutha.org or http://www.last-bastion.net.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase as ptc
from Products.ZScheduler.ZScheduleEvent import ZScheduleEvent

ZopeTestCase.installProduct('ZScheduler')

ptc.setupPloneSite(products=['ZScheduler'])


class TestScheduler(ptc.PloneTestCase):

    def afterSetUp(self):

        portal = self.app
        #portal = self.portal
        portal._setObject('event1', ZScheduleEvent('event1', 'testing', 'no callable'))
        portal._setObject('event2', ZScheduleEvent('event2', 'testing', 'no callable'))
        portal._setObject('event3', ZScheduleEvent('event3', 'testing', 'no callable'))

        self.event1 = portal.event1

    def testSetup(self):
        self.failUnless('ZSchedulerTool' in self.app.objectIds())

    def testQueueCore(self):
        self.assertEqual(self.portal.event1._active, False)
        self.assertEqual(self.portal.event1.active, False)

        catalog = self.app.ZSchedulerTool.queue
        self.assertEqual(len(catalog.searchResults()), 3)
        self.assertEqual(len(catalog.searchResults(active=False)), 3)

    def testSchedulerAPI(self):
        zscheduler = self.app.ZSchedulerTool
        self.assertEqual(len(zscheduler.events()), 0)
        self.assertEqual(len(zscheduler.events(active=True)), 0)
        self.assertEqual(len(zscheduler.events(active=False)), 3)

        self.event1.manage_editSchedule('EST', '5', '*', '*', '*','*', True)
        self.assertEqual(zscheduler.events(active=True), [self.event1])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestScheduler))
    return suite
