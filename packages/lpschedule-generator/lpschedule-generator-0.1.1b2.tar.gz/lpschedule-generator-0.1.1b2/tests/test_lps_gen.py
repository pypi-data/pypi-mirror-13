# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015  lpschedule-generator contributors. See CONTRIBUTORS.
#
#    This file is part of lpschedule-generator.
#
#   lpschedule-generator is free software: you can redistribute it
#   and/or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   lpschedule-generator is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with lpschedule-generator (see COPYING).  If not, see
#   <http://www.gnu.org/licenses/>.

import json
import pprint

import mistune
import mock

from os import path
from StringIO import StringIO

from nose.tools import *

from lps_gen import *

class TestLpsGen(object):
    """
    Class that tests the lps_gen.py module.
    """
    @classmethod
    def setup_class(self):
        """Runs before running any tests in this class."""

        self.MD_FILE = path.join('tests', 'files', 'lp-sch.md')
        self.MD_FILE_CONTENT = read_file(self.MD_FILE)

        self.SCH_TEMPLATE = path.join('tests', 'files',
                                      'lp-sch-2016.jinja2')

        self.markdown = LPSMarkdown()
        self.lps_dict = self.markdown(self.MD_FILE_CONTENT)

    def setup(self):
        """Runs before each test in this class."""
        pass


    def test_LPSMarkdown_day(self):
        """
        Testing `LPSMarkdown` class - Day.
        """
        days = ['Saturday, March 19',
                'Sunday, March 20']
        i = 0
        for day in self.lps_dict.keys():
            assert_equal(day, days[i])
            i = i + 1


    def test_LPSMarkdown_timeslot(self):
        """
        Testing `LPSMarkdown` class - Timeslot.
        """
        timeslots = [
            '09:00 - 09:45: Registration and Breakfast',
            '09:45 - 10:45: Opening Keynote: Richard Stallman',
            '10:55 - 11:40: Session Block 1A',
            '11:40 - 11:50: Break',
            '11:50 - 12:35: Session Block 2A',
            '09:00 - 09:45: Registration and breakfast',
            '09:45 - 10:30: Keynote: Benjamin Mako Hill',
            '10:30 - 10:40: Break',
            '10:40 - 11:25: Session Block 1B',
            ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for timeslot in lps_timeslots.keys():
                assert_equal(timeslot, timeslots[i])
                i = i + 1


    def test_LPSMarkdown_session(self):
        """
        Testing `LPSMarkdown` class - Session.
        """
        sessions = [
            'Free software, free hardware, and other things',
            'Federation and GNU',
            'Dr. Hyde and Mr. Jekyll: advocating for free software in nonfree academic contexts',
            'TAFTA, CETA, TISA: traps and threats to Free Software Everywhere',
            'Let\'s encrypt!',
            'Attribution revolution -- turning copyright upside-down',
            'Access without empowerment',
            'Fork and ignore: fighting a GPL violation by coding instead',
            'Who did this? Just wait until your father gets home',
            ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session in lps_sessions.keys():
                    assert_equal(session, sessions[i])
                    i = i + 1


    def test_LPSMarkdown_speaker(self):
        """
        Testing `LPSMarkdown` class - Speaker
        """
        speakers = [
            ['Richard Stallman'],
            ['<a href="http://dustycloud.org">Christopher Webber</a>'],
            ['ginger coons'],
            ['<a href="http://libreplanet.org/2015/program/speakers.html#corvellec">Marianne Corvellec</a>',
             '<a href="http://libreplanet.org/2015/program/speakers.html#le-lous">Jonathan Le Lous</a>'],
            ['Seth Schoen'],
            ['Jonas Öberg'],
            ['Benjamin Mako Hill'],
            ['Bradley Kuhn'],
            ['Ken Starks'],
            ]

        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    assert_equal(session_info['speakers'], speakers[i])
                    i = i + 1


    def test_LPSMarkdown_room(self):
        """
        Testing `LPSMarkdown` class - Room
        """
        rooms = [
            'Room 32-123',
            'Room 32-123',
            'Room 32-141',
            'Room 32-155',
            'Room 32-123',
            'Room 32-141',
            'Room 32-123',
            'Room 32-123',
            'Room 32-141',
            ]
        i = 0
        for lps_timeslots in self.lps_dict.values():
            for lps_sessions in lps_timeslots.values():
                for session_info in lps_sessions.values():
                    assert_equal(session_info['room'], rooms[i])
                    i = i + 1


    def test_RenderHTML(self):
        """Testing `RenderHTML` function
        """
        lps_html = RenderHTML(self.lps_dict, self.SCH_TEMPLATE)
        print lps_html


    def test_RenderHTML_sessions_only(self):
        """Testing `RenderHTML` function - sessions only
        """
        md_content = read_file(path.join('tests', 'files',
                                         'lp-sch-sessions-only.md'))

        lps_html = RenderHTML(self.markdown(md_content),
                              self.SCH_TEMPLATE)
        print lps_html

    @raises(SystemExit)
    def test_RenderHTML_nonexistent_template(self):
        """Testing `RenderHTML` function - with non-existent template
        """
        with mock.patch('sys.stdout', new_callable=StringIO) as out:
            nonexistent_template = 'lpsch-template.null'

            lps_html = RenderHTML(self.lps_dict, nonexistent_template)
            expected_out = 'Template %s not found.\n' % template_name
            assert out.getvalue() == expected_out


    def teardown(self):
        """Cleans up things after each test in this class."""
        pass


    @classmethod
    def teardown_class(self):
        """Purge the mess created by this test."""
        pass
