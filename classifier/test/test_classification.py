import unittest

import main


class TestVideoInfo(unittest.TestCase):

  info = """
Input #0, matroska,webm, from '/home/damien/epfl/mjf/videos/10STRA29A22XD.song19.mkv':
  Metadata:
    TIMECODE        : 12:49:07:01
    UID             : edf20100-9453-05c1-04c6-080046020125
    GENERATION_UID  : edf20100-9453-05c2-04c6-080046020125
    COMPANY_NAME    : SONY
    PRODUCT_NAME    : Opt 
    PRODUCT_VERSION : 1.22
    PRODUCT_UID     : 060e2b34-0401-0103-0e06-012002030300
    MODIFICATION_DATE: 2010-07-17 00:51:17
    MATERIAL_PACKAGE_UMID: 0x060A2B340101010501010D4313000000762901009453058008004602012504C6
    ENCODER         : Lavf56.33.101
  Duration: 00:06:38.80, start: 0.000000, bitrate: 30991 kb/s
    Stream #0:0: Video: h264 (High), yuv420p, 1920x1080 [SAR 1:1 DAR 16:9], 50 fps, 50 tbr, 1k tbn, 100 tbc
    Metadata:
      FILE_PACKAGE_UMID: 0x060A2B340101010501010D4313000000772901009453058008004602012504C6
      ENCODER         : Lavc56.39.101 libx264
    Stream #0:1: Audio: pcm_s24le, 48000 Hz, 2 channels, s32 (24 bit), 2304 kb/s (default)
    Metadata:
      ENCODER         : Lavc56.39.101 pcm_s24le"""

  def test_duration(self):
    duration = main.read_duration(self.info)
    self.assertTupleEqual(duration, (0, 6, 38, 80))

  def test_size(self):
    size = main.read_size(self.info)
    self.assertTupleEqual(size, (1920, 1080))

  def test_fps(self):
    fps = main.read_fps(self.info)
    self.assertEqual(fps, 50)

  def test_nframes(self):
    self.assertEquals(main.compute_nframes((0, 0, 1, 0), 50), 50)
    self.assertEquals(main.compute_nframes((0, 0, 1, 1), 50), 51)
    self.assertEquals(main.compute_nframes((0, 1, 0, 0), 50), 3000)
    self.assertEquals(main.compute_nframes((1, 0, 0, 0), 50), 180000)
