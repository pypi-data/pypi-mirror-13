import cgi
import chardet
import imghdr
import os
import urllib
import urllib2
import urlparse
import uuid

import lxml.html
import lxml.html.builder
import tempfile

import requests

def _build_html(node, encoding):
    root = lxml.html.builder.HTML(
            lxml.html.builder.HEAD(),
            lxml.html.builder.BODY()
            )
    encoding_string = '<meta charset="' + encoding + '">'
    encoding_node = lxml.html.fragment_fromstring(encoding_string)
    root[0].append(encoding_node)
    root[1].append(node)
    return root

def get_encoding_from_content(content_attribute_string):
    return 'utf8'

class NoUrlError(Exception):
    def __str__(self):
        return 'Chapter instance URL attribute is None'

class XPathNotFoundError(Exception):
    def __init__(self, xpath_string):
        self.xpath_string = xpath_string
    def __str__(self):
        return self.xpath_string + ' not found'

class ImageErrorException(Exception):
    def __init__(self, image_url):
        self.xpath_string = image_url
    def __str__(self):
        return 'Error downloading image from ' + self.xpath_string

class ContentEncodingError(Exception):
    def __init__(self, content_string):
        self.content_string = content_string
    def __str__(self):
        return self.content_string + " doesn't contain an encoding"

def open_from_path_or_url(path_or_url, base_url=None):
    #MODIFY TO READ IN IMAGES FROM PATHS
    full_image_url = urlparse.urljoin(base_url, path_or_url)
    read_image_file = urllib2.urlopen(full_image_url).read()
    return read_image_file

def save_image(image_url, image_path, image_output_name, base_website_url=None):
    _, temporary_image_file = tempfile.mkstemp()
    os.close(_)
    try:
        read_image_file = open_from_path_or_url(image_url, base_website_url)
    except Exception:
        raise ImageErrorException(image_url)
    with open(temporary_image_file, 'wb') as f:
        f.write(read_image_file)
    image_type = imghdr.what(temporary_image_file)
    os.remove(temporary_image_file)
    if image_type is not None:
        full_image_name = os.path.join(image_path, image_output_name + '.' + image_type)
        with open(full_image_name, 'wb') as f:
            f.write(read_image_file)
        return {'image type': image_type, 'full image name': full_image_name}
    else:
        raise ImageErrorException(image_url)

class Chapter():
    '''
    Represents a chapter for an epub
    Input html file as filepath string
    contains the following attributes:
        title -- title of chapter
        content -- content of chapter
        encoding -- content and title encoding
    '''
    def __init__(self, html_input, url, title=None):
        def _process_HTML_input(html_input):
            '''
            Takes in a file path or lxml.html.HtmlElement objtect
            Sets self.content to lxml.html.HtmlElement object
            '''
            if isinstance(html_input, basestring):
                self.content = lxml.html.parse(html_input).getroot()
            elif isinstance(html_input, lxml.html.HtmlElement):
                self.content = html_input
            else:
                raise TypeError
        def _process_title(title):
            '''
            Determines title or sets to that given
            self.title = unicode string of title
            self.HTML_title = HTML-safe title
            Uses cgi.escape to create HTML-safe title
            Assumes that self.content exists
            '''
            def convert_title(title_text):
                if title_text:
                    self.title = unicode(title_text)
                    self.HTML_title = cgi.escape(title_text, quote=True)
                else:
                    self.title = u'Default Title'
                    self.HTML_title = u'Default Title'
            if title is None:
                try:
                    title_text = self.content.xpath('//title')[0].text
                    convert_title(title_text)
                except IndexError:
                    convert_title('')
            else:
                assert isinstance(title, basestring)
                convert_title(title)
        def _process_encoding(html_input):
            try:
                charset_node = self.content.xpath('//meta[@charset]')[0]
                self.encoding = charset_node.attrib['charset'].lower()
                self.encoding_specified = True
            except IndexError:
                try:
                    content_node = self.content.xpath('//meta[@content]')[0]
                    content_string = content_node.attrib['content']
                    self.encoding = get_encoding_from_content(content_string)
                    self.encoding_specified = True
                except IndexError:
                    with open(html_input, 'rb') as f:
                        self.encoding = chardet.detect(f.read())['encoding'].lower()
                    self.encoding_specified = False
        _process_HTML_input(html_input)
        _process_title(title)
        _process_encoding(html_input)
        self.url = url
    def get_content(self):
        return lxml.html.tostring(self.content,
                doctype='<!DOCTYPE html>'.encode(self.encoding),
                encoding='unicode')
    def get_content_as_element(self):
        return self.content
    def get_url(self):
        if self.url is not None:
            return self.url
        else:
            raise NoUrlError()
    def replace_image(self, image_url, image_node, output_folder,
            local_folder_name, image_name = None):
        if image_name is None:
            image_name = str(uuid.uuid4())
        try:
            image_extension = save_image(image_url, output_folder,
                    image_name)['image type']
            image_node.attrib['src'] = 'images' + '/' + image_name + '.' + image_extension
        except ImageErrorException:
            image_node.getparent().remove(image_node)
    def _replace_images_in_chapter(self, image_folder, local_image_folder):
        image_url_list = self.get_content_as_element().xpath('//img')
        for image in image_url_list:
            local_image_path = image.attrib['src']
            full_image_path = urlparse.urljoin(self.get_url(), local_image_path)
            self.replace_image(full_image_path, image, image_folder,
                    local_image_folder)
    def clean(self, start_node_xpath_string=None):
        '''
        Takes in an html file and a version stripped of unsuitable tags for an epub
        if start_node_xpath_string is not None, removes all content not contained
        in start_node_xpath_string.
        start_node_xpath_string should be inputted as an string representing the
        xpath path.
        If the evaluation of start_node__xpath_string returns a non-empty list,
        return first element
        '''
        def clean_node(lxml_node):
            filter_list = ('a', 'article', 'b', 'big', 'blockquote', 'body', 'br', 'center', 'cite',
                           'dd', 'del', 'dfn', 'div', 'dl', 'dt', 'em', 'font', 'footer', 'h1', 'h2',
                           'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'i', 'img', 'li', 'ol',
                           'p', 's', 'small', 'span', 'strike', 'strong', 'sub', 'sup',
                           'id', 'u', 'ul', 'var')
            for child in lxml_node.getchildren():
                if child.tag == 'a':
                    try:
                        child.attrib.pop('href')
                    except:
                        pass
                    clean_node(child)
                elif child.tag in filter_list:
                    clean_node(child)
                else:
                    child.drop_tree()
        if start_node_xpath_string is None:
            try:
                self.clean('//article')
            except XPathNotFoundError:
                clean_node(self.content)
                encoding_string = '<meta charset="' + self.encoding + '">'
                encoding_node = lxml.html.fragment_fromstring(encoding_string)
                self.content[0].append(encoding_node)
        else:
            try:
                evaluation_of_xpath = self.content.xpath(start_node_xpath_string)[0]
            except IndexError:
                raise XPathNotFoundError(start_node_xpath_string)
            if type(evaluation_of_xpath) == 'list':
                start_node = evaluation_of_xpath[0]
            else:
                assert type(evaluation_of_xpath) == lxml.html.HtmlElement
                start_node = evaluation_of_xpath
            clean_node(start_node)
            self.content = _build_html(start_node, self.encoding)
    def clean_and_replace_images(self, epub_instance,
            start_node_xpath_string=None):
        self.clean(start_node_xpath_string)
        self._replace_images_in_chapter(epub_instance.IMAGE_DIR,
                epub_instance.LOCAL_IMAGE_DIR)
    def write(self, file_name):
        with open(file_name, 'wb') as f:
            f.write(self.get_content().encode(self.encoding))
    def write_to_xhtml(self, file_name):
        content_string = u'<?xml verstion="1.0" encoding="UTF-8"?>' + self.get_content()
        with open(file_name, 'wb') as f:
            f.write(content_string.encode(self.encoding))
