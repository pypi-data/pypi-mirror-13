import os
import unittest
import xml.etree.ElementTree as ET

from pymediainfo import MediaInfo

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class MediaInfoTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(data_dir, 'sample.xml'), 'r') as f:
            self.xml_data = f.read()

    def test_populate_tracks(self):
        xml = ET.fromstring(self.xml_data)
        mi = MediaInfo(xml)
        self.assertEqual(4, len(mi.tracks))

    def test_valid_video_track(self):
        xml = ET.fromstring(self.xml_data)
        mi = MediaInfo(xml)
        for track in mi.tracks:
            if track.track_type == 'Video':
                self.assertEqual('DV', track.codec)
                self.assertEqual('Interlaced', track.scan_type)
                break

    def test_track_integer_attributes(self):
        xml = ET.fromstring(self.xml_data)
        mi = MediaInfo(xml)
        for track in mi.tracks:
            if track.track_type == 'Audio':
                self.assertTrue(isinstance(track.duration, int))
                self.assertTrue(isinstance(track.bit_rate, int))
                self.assertTrue(isinstance(track.sampling_rate, int))
                break

    def test_track_other_attributes(self):
        xml = ET.fromstring(self.xml_data)
        mi = MediaInfo(xml)
        for track in mi.tracks:
            if track.track_type == 'General':
                self.assertEqual(5, len(track.other_file_size))
                self.assertEqual(4, len(track.other_duration))
                break

    def test_load_mediainfo_from_string(self):
        mi = MediaInfo(self.xml_data)
        self.assertEqual(4, len(mi.tracks))

    def test_getting_attribute_that_doesnot_exist(self):
        mi = MediaInfo(self.xml_data)
        self.assertTrue(mi.tracks[0].does_not_exist is None)


class MediaInfoInvalidXMLTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(data_dir, 'invalid.xml'), 'r') as f:
            self.xml_data = f.read()

    def test_parse_invalid_xml(self):
        mi = MediaInfo(MediaInfo.parse_xml_data_into_dom(self.xml_data))
        self.assertEqual(len(mi.tracks), 0)

class MediaInfoLibraryTest(unittest.TestCase):
    def setUp(self):
        self.mi = MediaInfo.parse(os.path.join(data_dir, "sample.mp4"))
    def test_track_count(self):
        self.assertEqual(len(self.mi.tracks), 3)
    def test_track_types(self):
        self.assertEqual(self.mi.tracks[1].track_type, "Video")
        self.assertEqual(self.mi.tracks[2].track_type, "Audio")
    def test_track_details(self):
        self.assertEqual(self.mi.tracks[1].codec, "AVC")
        self.assertEqual(self.mi.tracks[2].codec, "AAC LC")
        self.assertEqual(self.mi.tracks[1].duration, 958)
        self.assertEqual(self.mi.tracks[2].duration, 980)
