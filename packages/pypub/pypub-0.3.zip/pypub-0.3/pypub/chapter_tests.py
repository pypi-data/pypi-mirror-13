import copy
import unittest
import os
import os.path
import tempfile

import lxml.html

import chapter
from constants import *

class TestBuild(unittest.TestCase):
    def test_build(self):
        start_node = lxml.html.fragment_fromstring('<p>TEST</p>')
        full_html = chapter._build_html(start_node, 'utf-8')
        chapter_object = chapter.Chapter(full_html)
        assert chapter_object.get_content().startswith('<!DOCTYPE html>')
        assert chapter_object.get_content_as_element()[1][0].text == 'TEST'
        assert chapter_object.get_content_as_element()[1][0].tag == 'p'

class ChapterTests(unittest.TestCase):
    def setUp(self):
        self.test_file_directory = os.path.join(TEST_DIR, 'test_chapters')
        self.output_file_directory = os.path.join(self.test_file_directory, 'test_output')
        self.test_chapter_list = []
        for index, html_file_path in enumerate(os.listdir(self.test_file_directory)):
            full_path = os.path.join(self.test_file_directory, html_file_path)
            if os.path.isfile(full_path):
                if index != 2:
                    self.test_chapter_list.append(chapter.Chapter(full_path))
                else:
                    title = 'Dummy Title &<>"'
                    self.test_chapter_list.append(chapter.Chapter(full_path, title))
    def test_title(self):
        assert self.test_chapter_list[0].title == u'Quick Practical, Tactical Tips for Presentations'
        assert self.test_chapter_list[0].HTML_title == u'Quick Practical, Tactical Tips for Presentations'
        assert self.test_chapter_list[1].HTML_title == u'Venture capital - Wikipedia, the free encyclopedia'
        assert self.test_chapter_list[1].title == u'Venture capital - Wikipedia, the free encyclopedia'
        assert self.test_chapter_list[2].title == 'Dummy Title &<>"'
        assert self.test_chapter_list[2].HTML_title == u'Dummy Title &amp;&lt;&gt;&quot;'
        assert self.test_chapter_list[3].title == u"The capture of Mosul: Terror\u2019s new headquarters | The Economist"
        assert self.test_chapter_list[3].HTML_title == u"The capture of Mosul: Terror\u2019s new headquarters | The Economist"
    def test_encoding(self):
        assert self.test_chapter_list[0].encoding == 'utf-8'
        assert self.test_chapter_list[0].encoding_specified is True
        assert self.test_chapter_list[1].encoding == 'utf-8'
        assert self.test_chapter_list[1].encoding_specified is True
        assert self.test_chapter_list[2].encoding == 'utf-8'
        assert self.test_chapter_list[2].encoding_specified is True
        assert self.test_chapter_list[3].encoding == 'utf-8'
        assert self.test_chapter_list[3].encoding_specified is True
    def test_get_encoding_from_content(self):
        assert chapter.get_encoding_from_content('text/html; charset=utf-8') == 'utf-8'
        assert chapter.get_encoding_from_content('text/html; charset = utf-8') == 'utf-8'
        assert chapter.get_encoding_from_content('text/html; charset = utf-8 ') == 'utf-8'
        assert chapter.get_encoding_from_content('text/html; charset = UTF-8 ') == 'utf-8'
        assert chapter.get_encoding_from_content('text/html; charset=ascii') == 'ascii'
    def test_clean(self):
        for index, chapter_object in enumerate(self.test_chapter_list):
            chapter_object.clean()
            charset_xpath_expression = '//*[contains(@charset,' + '"' + chapter_object.encoding + '")]'
            assert len(chapter_object.content.xpath(charset_xpath_expression)) == 1
            output_file_name = os.path.join(self.output_file_directory, str(index) + '.html')
            chapter_object.write(output_file_name)

class ImageTests(unittest.TestCase):
##    def test_image_type(self):
##        test_image_input_folder = os.path.join(TEST_DIR, 'test_images')
##        image_file_path_list = [
##            os.path.join(test_image_input_folder,'0.png'),
##            os.path.join(test_image_input_folder,'1.jpeg'),
##            ]
##        test_image_output_folder = tempfile.mkdtemp()
##        for index , image_url in enumerate(image_file_path_list):
##            image_type = chapter.save_image(image_url, test_image_output_folder, str(index))
##            if index == 0:
##                assert image_type['image type'] == 'png'
##            if index == 1:
##                assert image_type['image type'] == 'jpeg'
    def test_create_chapter_with_images(self):
        test_page_folder = os.path.join(TEST_DIR, 'test_page')
        test_page = 'http://www.bothsidesofthetable.com/2014/10/15/when-should-technical-founders-become-ceo/'
        test_page_output_folder = os.path.join(test_page_folder, 'output')
        test_page_image_output_folder = os.path.join(test_page_output_folder, 'images')
        c = chapter.Chapter(test_page, url = test_page_folder)
        c.clean_and_replace_images(image_folder=test_page_image_output_folder,
                local_image_folder='images')
        full_output_name = os.path.join(test_page_output_folder, 'output.html')
        c.write(full_output_name)
        output_chapter = chapter.Chapter(full_output_name)
if __name__ == '__main__':
    unittest.main()
