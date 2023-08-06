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

class TestLPS(object):
    """
    Class that tests everything related LP Schedule.
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
        """Testing `RenderHTML` function with LP schedule
        """
        lps_html = RenderHTML(self.lps_dict, self.SCH_TEMPLATE)
        print lps_html


    def test_RenderHTML_sessions_only(self):
        """Testing `RenderHTML` function - LP schedule - sessions only
        """
        md_content = read_file(path.join('tests', 'files',
                                         'lp-sch-sessions-only.md'))

        lps_html = RenderHTML(self.markdown(md_content),
                              self.SCH_TEMPLATE)
        print lps_html

    @raises(SystemExit)
    def test_RenderHTML_nonexistent_template(self):
        """Testing `RenderHTML` function - LP schedule - ith non-existent template
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


class TestLPSpeakers(object):
    """
    Class that tests everything related LP Speakers
    """

    @classmethod
    def setup_class(self):
        """Runs before running any tests in this class."""

        self.MD_FILE = path.join('tests', 'files', 'lp-speakers.md')
        self.MD_FILE_CONTENT = read_file(self.MD_FILE)

        self.SPEAKERS_TEMPLATE = path.join('tests', 'files',
                                           'lp-speakers-2016.jinja2')

        self.markdown = LPSpeakersMarkdown()
        self.lpspeakers_dict = self.markdown(self.MD_FILE_CONTENT)


    def setup(self):
        """Runs before each test in this class."""
        pass


    def test_LPSpeakersMarkdown_keynotespeakers_name(self):
        """Testing LPSpeakersMarkdown keynote speakers' names.

        """
        keynote_speakers = ['Daniel Kahn Gillmor',
                            'Edward Snowden',
                            'Richard Stallman',
                            'Clara Snowden',
                            'Ludovic Courtès']

        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            assert_equal(kspeaker['speaker'], keynote_speakers[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_id(self):
        """Testing LPSpeakersMarkdown keynote speakers' id.

        """
        keynote_speaker_ids = ['gillmor',
                               'snowden',
                               'stallman',
                               'clara_snowden',
                               'courtes']


        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            assert_equal(kspeaker['id'], keynote_speaker_ids[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_imgurl(self):
        """Testing LPSpeakersMarkdown keynote speakers' image url.

        """
        keynote_speaker_img_urls = ['//static.fsf.org/nosvn/libreplanet/speaker-pics/dkg.jpg',
                                    '//static.fsf.org/nosvn/libreplanet/speaker-pics/snowden.jpg',
                                    '//static.fsf.org/nosvn/libreplanet/speaker-pics/stallman.jpg',
                                    '//static.fsf.org/nosvn/libreplanet/speaker-pics/c_snowden.jpg']



        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            if kspeaker.has_key('img_url'):
                assert_equal(kspeaker['img_url'],
                             keynote_speaker_img_urls[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_imgalt(self):
        """Testing LPSpeakersMarkdown keynote speakers' image alt text.

        """

        keynote_speaker_img_alts = ['Daniel Kahn Gillmor - Photo',
                                    'Edward Snowden - Photo',
                                    'Richard Stallman - Photo',
                                    '']



        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            if kspeaker.has_key('img_alt'):
                assert_equal(kspeaker['img_alt'],
                             keynote_speaker_img_alts[i])
            i = i + 1


    def test_LPSpeakersMarkdown_keynotespeakers_bio(self):
        """Testing LPSpeakersMarkdown keynote speakers' bio.

        """

        keynote_speaker_bios = [['Daniel Kahn Gillmor is a technologist with the ACLU\'s Speech, Privacy'],
                                ['Edward Snowden is a former intelligence officer who served the CIA,'],
                                ['Richard is a software developer and software freedom activist. In 1983',
                                 'Since the mid-1990s, Richard has spent most of his time in political',],
                                [],

                                ['Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam',
                                 'Ut turpis felis, pulvinar a semper sed, adipiscing id']]


        i = 0
        for kspeaker in self.lpspeakers_dict['keynote-speakers']:
            if kspeaker.has_key('bio'):
                j = 0
                for p in kspeaker['bio']:
                    p.startswith(keynote_speaker_bios[i][j])
                    j = j + 1

            i = i + 1


    def test_LPSpeakersMarkdown_speakers_name(self):
        """Testing LPSpeakersMarkdown speakers' names.

        """
        speakers = ['Emmanuel',
                    'George Chriss',
                    'Marianne Corvellec',
                    'Richard Fontana',
                    'Mike Gerwitz',
                    'Bassam Kurdali',
                    'Jonathan Le Lous',
                    'M. C. McGrath',
                    'Deb Nicholson',
                    'Stefano Zacchiroli']

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            assert_equal(kspeaker['speaker'], speakers[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_id(self):
        """Testing LPSpeakersMarkdown speakers' id.

        """
        speaker_ids = ['emmanuel',
                       'chriss',
                       'corvellec',
                       'fontana',
                       'gerwitz',
                       'kurdali',
                       'lous',
                       'mcgrath',
                       'nicholson',
                       'zacchiroli']

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            assert_equal(kspeaker['id'], speaker_ids[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_imgurl(self):
        """Testing LPSpeakersMarkdown speakers' image url.

        """
        speaker_img_urls = ['', '',
                            '//static.fsf.org/nosvn/libreplanet/speaker-pics/corvellec.jpg',
                            '', '',
                            '//static.fsf.org/nosvn/libreplanet/speaker-pics/kurdali.png',
                            '//static.fsf.org/nosvn/libreplanet/speaker-pics/lelous.jpg',
                            '',
                            '//static.fsf.org/nosvn/libreplanet/speaker-pics/nicholson.jpg',
                            '//static.fsf.org/nosvn/libreplanet/speaker-pics/zacchiroli.jpg']

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            if kspeaker.has_key('img_url'):
                assert_equal(kspeaker['img_url'],
                             speaker_img_urls[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_imgalt(self):
        """Testing LPSpeakersMarkdown speakers' image alt text.

        """
        speaker_img_alts = ['', '',
                            'Marianne Corvellec - Photo',
                            '', '',
                            'Bassam Kurdali - Photo',
                            'Jonathan Le Lous - Photo',
                            '',
                            'Deb Nicholson - Photo',
                            'Stefano Zacchiroli - Photo']



        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            if kspeaker.has_key('img_alt'):
                assert_equal(kspeaker['img_alt'],
                             speaker_img_alts[i])
            i = i + 1


    def test_LPSpeakersMarkdown_speakers_bio(self):
        """Testing LPSpeakersMarkdown speakers' bio.

        """
        speaker_bios = [['Emmanuel is a Division III student at Hampshire College, studying how'],
                        [],
                        ['Marianne Corvellec has been a Free Software activist with April'],
                        ['Richard Fontana is a lawyer at Red Hat. He leads support for Red Hat\'s'],
                        [],
                        ['Bassam is a 3D animator/filmmaker whose 2006 short, Elephants Dream,'],
                        ['Jonathan has been involved with the Free Software Movement for ten'],
                        ['M. C. is the founder of Transparency Toolkit, a free software project'],
                        [],
                        ['Stefano Zacchiroli is Associate Professor of Computer Science at']]

        i = 0
        for kspeaker in self.lpspeakers_dict['speakers']:
            if kspeaker.has_key('bio'):
                j = 0
                for p in kspeaker['bio']:
                    p.startswith(speaker_bios[i][j])
                    j = j + 1

            i = i + 1


    def test_RenderHTML(self):
        """Testing `RenderHTML` function with LP speakers
        """
        lps_html = RenderHTML(self.lpspeakers_dict, self.SPEAKERS_TEMPLATE)
        print lps_html


    def teardown(self):
        """Cleans up things after each test in this class."""
        pass


    @classmethod
    def teardown_class(self):
        """Purge the mess created by this test."""
        pass
