# -*- coding:utf-8 -*-
import re
import logging
from xml import sax
from xml.sax.xmlreader import InputSource
from cStringIO import StringIO

from lxml import etree

from .text_handler import TextHandler, NewTextHandler, ErrorHandler


def extract(html):
    return extract_tag_texts(html, handler=NewTextHandler)


def extract_tag_texts(html_content, handler=TextHandler):
    """
    :param html_content: str
    :param handler: ContentHandler's subclass

    :return: {
        'a':{
            'texts: [str]
            'words_count': int
        }
    }
    """
    html = clean_html(html_content)
    parser = sax.make_parser()
    parser.setContentHandler(handler())
    parser.setErrorHandler(ErrorHandler())
    parser.setFeature("http://xml.org/sax/features/external-general-entities", False)

    inpsrc = InputSource()
    inpsrc.setByteStream(StringIO(html))

    parser.parse(inpsrc)
    return parser.getContentHandler().result


def clean_html(html_content):
    html = html_content
    html = re.sub(u'<!DOCTYPE[^>]*>(?isu)', '', html)
    shtml = re.split(u'<html[^>]*>', html)
    html = '<html>' + shtml[1] if len(shtml) == 2 else html
    html = re.sub(u'<style[^>]*>.*?</style>(?isu)', '', html)
    html = re.sub(u'<script[^>]*>.*?</script>(?isu)', '', html)
    html = re.sub(u'<link[^>]*>', '', html)
    html = re.sub(u'<base[^>]*>', '', html)
    html = re.sub(u'<script[^>]*>', '', html)
    html = re.sub(u'<noindex[^>]*>.*?</noindex>(?isu)', '', html)
    html = re.sub(u'<!--[\s]*noindex[\s]*-->.*?<!--[\s]*/noindex[\s]*-->(?isu)', '', html)
    html = re.sub(u'<noscript[^>]*>.*?</noscript>(?isu)', '', html)
    html = re.sub(u'<!--.*?-->(?isu)', '', html)
    html = re.sub(u'<select[^>]*>.*?</select>(?isu)', ' ', html)
    html = re.sub(u'<(option)[^>]*>.*?</\\1>(?isu)', ' ', html)
    html = re.sub(u'<textarea[^>]*>.*?</textarea>(?isu)', ' ', html)
    html = re.sub(u'&[^;]{2,10};(?isu)', ' ', html)
    html = re.sub(u'&#[a-z0-9]{1,10};(?isu)', ' ', html)
    html = re.sub(u'<!\[CDATA\[', '', html)
    html = re.sub(u']]><', '<', html)
    try:
        parser = etree.HTMLParser(recover=True, encoding='UTF-8')
        tree = etree.parse(StringIO(html), parser)
        root = tree.getroot()
        if root is not None:
            html = etree.tostring(root, encoding='UTF-8')
    except Exception as e:
        logging.warning(e, exc_info=1)
        html = ""
    return html
