# -*- coding: utf-8 -*-
"""
nidaba.tei
~~~~~~~~~~

A module for interfacing TEI OCR output
"""

from __future__ import absolute_import, division, print_function

from lxml import etree
from lxml.etree import Element, SubElement

from collections import OrderedDict
from functools import partial
from copy import deepcopy

from nidaba.nidabaexceptions import NidabaTEIException, NidabaRecordException


def _parse_hocr(title):
    """
    Parses the hOCR title string and returns a dictionary containing its
    contents.
    """
    def int_float_or_str(s):
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                try:
                    return unicode(s)
                except UnicodeDecodeError:
                    return s

    out = {}
    props = [x.strip() for x in title.split(';')]
    for prop in props:
        p = prop.split()
        out[p[0]] = tuple(int_float_or_str(x) for x in p[1:])
    return out


class OCRRecord(object):
    """
    A composite object of containing recognition results for a single scanned
    page.

    A page is divided into lines which may contain segments and graphemes. For
    practical purposes this means that the appropriate line or segment (the
    later overriding the first) has to be brought into scope first before
    adding any characters to it.
    
    Each element may be associated with a responsibility statement, identifying
    the origin of each alteration if the final serialization supports it.
    """

    # automatically generated properties on the class
    fields = ['title', 'author', 'editor', 'funder', 'principal', 'sponsor',
              'meeting', 'edition', 'publisher', 'distributor', 'authority',
              'idno', 'pub_place', 'licence', 'series_title', 'note',
              'source_desc', 'meta_language']

    def __init__(self):
        self.meta = {}
        self.respstmt = OrderedDict()
        self.resp_scope = None
        self.line_scope = None
        self.segment_scope = None

        self.lines = OrderedDict()

    # generic setter/getter for metadata
    def _generic_getter(self, field):
        if field in self.meta:
            return self.meta[field]
        else:
            return None

    def _generic_setter(self, value, field):
        self.meta[field] = value

    # 
    # responsibility statement functionality
    def add_respstmt(self, resp, name, **kwargs):
        """
        Adds a responsibility statement and returns its identifier.

        The new responsibility statement is automatically scoped.
        Args:
            resp (unicode): Nature of the responsible process.
            name (unicode): Text describing the processing software.
            kwargs (dict): Additional data used be the final serialization.

        Returns:
            A string containing the respstmt ID.
        """
        kwargs['resp'] = resp
        kwargs['name'] = name
        id = u'resp_' + unicode(len(self.respstmt) + 1)
        self.respstmt[id] = kwargs
        self.resp_scope = id
        return id

    def scope_respstmt(self, id):
        """
        Scopes a responsibility statement.

        Args:
            id (unicode): String of targeted resposibility statement.

        Raises:
            NidabaRecordException if the responsibility statement couldn't be
            found.
        """
        if id not in self.respstmt:
            raise NidabaRecordException('No such responsibility statement')
        self.resp_scope = id

    def reset_respstmt_scope(self):
        """
        Clears the current responsibility scope.
        """
        self.resp_scope = None

    #  writer functions for topographical data
    def add_line(self, dim, **kwargs):
        """
        Marks the start of a new topographical line and scopes it.

        Args:
            dim (tuple): A tuple (x0, y0, x1, y1) denoting the bounding box.
            kwargs (dict): Additional data used by the final serialization.

        Returns:
            A string containing the line's identifier.
        """
        id = u'line_' + unicode(len(self.lines) + 1)
        kwargs['bbox'] = dim
        kwargs['content'] = OrderedDict()
        if self.resp_scope:
            kwargs['resp'] = self.resp_scope
        self.lines[id] = kwargs
        self.line_scope = id
        return id

    def add_segment(self, dim, language=None, confidence=None, **kwargs):
        """
        Marks the beginning of a new topographical segment in the current
        scope. Most often this correspond to a word recognized by an engine.

        Args:
            dim (tuple): A tuple containing the bounding box (x0, y0, x1, y1)
            lang (unicode): Optional identifier of the segment language.
            confidence (float): Optional confidence value between 0 and 100.
            kwargs (dict): Additional data used by the final serialization.

        Returns:
            A string containing the segment's indeitifier.

        Raises:
            NidabaRecordException if no line is scoped.
        """
        if not self.line_scope:
            raise NidabaRecordException('No line scoped.')
        id = u'seg_' + unicode(len(self.segments) + 1)
        kwargs['type'] = 'segment'
        kwargs['bbox'] = dim
        if language:
            kwargs['language'] = language
        if confidence:
            kwargs['confidence'] = confidence
        if self.resp_scope:
            kwargs['resp'] = self.resp_scope

        kwargs['content'] = OrderedDict()
        self.lines[self.line_scope]['content'][id] = kwargs
        self.segment_scope = id
        return id

    # actual recognition result writer
    def add_graphemes(self, it):
        """
        Adds a number of graphemes to the current scope (either line or segment).

        A line and/or segment has to be created beforehand.

        Args:
            it (iterable): An iterable returning a dictionary which at least
                           contains a key 'grapheme' with the recognition
                           result. A bounding box has to be placed under the
                           key 'bbox'; a confidence value in the range 0-100
                           (float) is expected under 'confidence'. Additional
                           data (style etc.) will be retained for serializer
                           use.
        """
        if self.line_scope is None:
            raise NidabaRecordException('No element scoped.')
        if self.segment_scope is not None:
            target = self.lines[self.line_scope]['content'][self.segment_scope]['content']
        else:
            target = self.lines[self.line_scope]['content']
        gr_cnt = len(self.graphemes)
        for glyph in it:
            gr_cnt += 1
            id = u'grapheme_' + unicode(gr_cnt)
            glyph['type'] = 'grapheme'
            if 'grapheme' not in glyph:
                raise NidabaRecordException('Mandatory field missing when adding graphemes.')
            if self.resp_scope:
                glyph['resp'] = self.resp_scope
            target[id] = glyph

    
    def add_choices(self, id, it):
        """
        Adds alternative interpretations to an element.

        Args:
            id (unicode): ID of the element.
            it (iterable): An iterable returning a dictionary containing an
            alternative reading ('alternative') and an optional confidence
            value ('confidence') in the range between 0 and 100.

        Raises:
            NidabaRecordException if no element with the ID could be found.
        """
        if id in self.lines:
            target = self.lines[id]
        for line in self.lines.itervalues():
            if id in line['content']:
                target = line['content'][id]
                break
            for seg in line['content'].itervalues():
                if 'content' in seg and id in seg['content']:
                    target = seg['content'][id]
                    break
        alt = {'content': list(it)}
        if self.resp_scope:
            alt['resp'] = self.resp_scope
        target['alternatives'] = alt

    # scoping of topographical elements
    def scope_line(self, id):
        """
        Scopes a line.

        Args:
            id (unicode): ID of the line to scope.

        Raises:
            NidabaRecordException if no line with the ID could be found.
        """
        if id not in self.lines:
            raise NidabaRecordException('Invalid line ID.')
        self.line_scope = id

    def scope_segment(self, id):
        """
        Scopes a segment (and by association its line).

        Args:
            id (unicode): ID of the segment to scope.

        Raises
        """
        for line in self.lines.itervalues():
            if id in line['content']:
                self.line_scope = line
                self.segment_scope = id
                return
        raise NidabaRecordException('Invalid segment ID.')

    def reset_line_scope(self):
        """
        Resets line scope.
        """
        self.line_scope = None

    def reset_segment_scope(self):
        """
        Resets segment scope.
        """
        self.segment_scope = None

    # clearing topographical data
    def clear_lines(self):
        """
        Deletes all lines and their content from the record.
        """
        self.reset_line_scope()
        self.lines = OrderedDict()

    def clear_segments(self):
        """
        Deletes all segments and their content from the record.
        """

        self.reset_segment_scope()
        self.segment_scope = None
        for line in self.lines.itervalues():
            line['content'] = OrderedDict()

    # properties offering short cuts (line are already top-level records)
    @property
    def segments(self):
        """
        Returns an OrderedDict of segments with each segment being a dictionary.
        """
        seg = OrderedDict()
        for line in self.lines.itervalues():
            for el in line['content'].itervalues():
                if el['type'] == 'segment':
                    seg.append(el)
        return seg

    @property
    def graphemes(self):
        """
        Returns a list of graphemes with each grapheme being a dictionary.
        """
        g = OrderedDict()
        for line in self.lines.itervalues():
            for el in line['content'].itervalues():
                if el['type'] == 'segment':
                    g.extend(el['content'].itervalues())
                elif el['type'] == 'grapheme':
                    g.append(el)
        return g

    # de-/serializers
    def load_tei(self, fp):
        doc = etree.parse(fp)

        self.respstmt = OrderedDict()
        self.resp_scope = None

        for resp in doc.iter(self.tei_ns + 'respstmt'):
            id = resp.get(self.xml_ns + 'id')
            r = resp.find('.//{}resp'.format(self.tei_ns)).text
            n = resp.find('.//{}name'.format(self.tei_ns)).text
            respstmt[id] = {'resp': r, 'name': n}

        root_zone = doc.find('/TEI/sourceDoc/surface/zone')

        choice_flag = False
        sic_flag = False
        sic_content = []
        corr_flag = True
        corrections = []
        last_el = None
        for el in root_zone.iter():
            if el.tag == 'choice':
                pass
            elif el.tag == 'sic':
                pass
            elif el.tag == 'corr':
                pass
            elif el.tag == 'line':
                if el.get('resp'):
                    self.scope_respstmt(el.get('resp')[1:])
                self.add_line((int(el.get('ulx')), int(el.get('uly')),
                               int(el.get('lrx')), int(el.get('lry'))))
            elif el.tag == 'zone' and el.get('type') == 'segment':
                if el.get('resp'):
                    self.scope_respstmt(el.get('resp')[1:])
                self.add_segment((int(el.get('ulx')), int(el.get('uly')),
                                  int(el.get('lrx')), int(el.get('lry'))))
            elif el.tag == 'zone' and el.get('type') == 'grapheme':
                self.add_segment((int(el.get('ulx')), int(el.get('uly')),
                                  int(el.get('lrx')), int(el.get('lry'))))
            elif el.tag == 'certainty':
                last_el['certainty'] = float(el.get('degree')) * 100
            elif el.tag in ['seg', 'g']:
                pass
            else:
                raise NidabaRecordException('Unknown tag {} encountered'.format(el.tag))

    def write_tei(self, fp):
        doc = Element('TEI', nsmap={None: 'http://www.tei-c.org/ns/1.0'},
                      version='5.0')
        header = SubElement(doc, self.tei_ns + 'teiHeader')
        fileDesc = SubElement(header, self.tei_ns + 'fileDesc')
        titleStmt = SubElement(fileDesc, self.tei_ns + 'titleStmt')
        pubStmt = SubElement(fileDesc, self.tei_ns + 'publicationStmt')

        sourceDoc = SubElement(self.doc, self.tei_ns + 'sourceDoc')
        surface = SubElement(sourceDoc, self.tei_ns + 'surface', ulx='0', uly='0', lrx=str(dim[0]), lry=str(dim[1]))
        SubElement(surface, self.tei_ns + 'graphic', url=image_url)
        surface_zone = SubElement(surface, self.tei_ns + 'zone')

        for id, resp in self.respstmt:
            r = SubElement(titleStmt, self.tei_ns + 'respStmt')
            r.set(self.xml_ns + 'id', id)
            SubElement(r, self.tei_ns + 'resp').text = resp['resp']
            SubElement(r, self.tei_ns + 'name').text = resp['name']

        def _set_confidence(el, up, dic):
            if 'confidence' in dic:
                cert = SubElement(el, self.tei_ns + 'certainty',
                                  degree=u'{0:.2f}'.format(alt['confidence'] / 100.0), 
                                  locus='value', target='#' + el.get(self.xml_ns + 'id'))
            if 'resp' in up:
                el.set('resp', '#' + up['resp'])
                if cert is not None:
                    cert.set('resp', '#' + up['resp'])

        def _wrap_choices(alternatives, sic, parent):
            choice = SubElement(parent, self.tei_ns + 'choice')
            sic_el = SubElement(choice, self.tei_ns + 'sic')
            sic_el.append(sic)
            for alt in alternatives['content']:
                corr = SubElement(choice, self.tei_ns + 'corr')
                corr.text = alt['alternative']
                _set_confidence(corr, alternatives, alt)

        def _add_grapheme(grapheme_id, grapheme, parent):
            g_el = Element(self.tei_ns + 'zone',
                           ulx=str(), uly=str(), lrx=str(),
                           lry=str(), type='grapheme')
            g_el.set(self.xml_ns + 'id', grapheme_id)
            if 'alternatives' in grapheme:
                _wrap_choice(grapheme['alternatives'], g_el, parent)
            else:
                parent.append(g_el)
            glyph = SubElement(SubElement(g_el, self.tei_ns + 'seg'), self.tei_ns + 'g')
            glyph.text = grapheme['grapheme']
            _set_confidence(g_el, grapheme, grapheme)

        for line_id, line in self.lines.iteritems():
            line_el = Element(self.tei_ns + 'line', ulx=str(), uly=str(),
                              lrx=str(), lry=str()) 
            line_el.set(self.xml_ns + 'id', line_id)
            if 'alternatives' in line:
                _wrap_choice(line['alternatives'], line_el, surface_zone)
            else:
                surface_zone.append(line_el)
            for seg_id, seg in line['content'].iteritems():
                _set_confidence(seg_el, seg, seg)
                if seg['type'] == 'segment':
                    seg_el = Element(self.tei_ns + 'zone',
                                     ulx=str(), uly=str(), lrx=str(),
                                     lry=str(), type=seg['type'])
                    seg_el.set(self.xml_ns + 'id', seg_id)
                    for grapheme_id, grapheme in seg['content'].iteritems():
                        _add_grapheme(grapheme_id, grapheme, seg_el)
                    if 'alternatives' in seg:
                        _wrap_choice(seg['alternatives'], seg_el, line_el)
                    else:
                        line_el.append(seg_el)
                elif seg['type'] == 'grapheme':
                    _add_grapheme(seg_id, seg, line_el)
                else:
                    raise NidabaRecordException('Unknown nodes beneath line records')
        fp.write(etree.tostring(page, xml_declaration=True, encoding='utf-8'))
        fp.flush()

    def write_abbyyxml(self, fp):
        """
        Writes the TEI document in a format reminiscent of Abbyy FineReader's
        XML output. Its basic format is:

        <text>
        <line l="0" r="111" t="6" b="89">
        <charParams l="0" r="78" t="6" b="89" charConfidence="76" wordStart="true">D</charParams>
        <charParams l="86" r="111" t="24" b="89" charConfidence="76" wordStart="false">e</charParams>
        </line>
        ....
        </text>

        Please note that alternative readings as produced for example by spell
        checking are dropped from the output. 

        Args:
            fp (file): File descriptor to write to.
        """
        page = Element('document')
        p = SubElement(page, 'page')
        surface = self.doc.find('.//{0}sourceDoc/{0}surface'.format(self.tei_ns))
        p.set('width', surface.get('lrx'))
        p.set('height', surface.get('lry'))
        p.set('originalCoords', '1')
        text = SubElement(p, 'text')
        last_seg_id = None
        for line in self.lines.itervalues():
            lel = SubElement(text, 'line')
            lel.set('l', int(line['bbox'][0]))
            lel.set('t', int(line['bbox'][1]))
            lel.set('r', int(line['bbox'][2]))
            lel.set('b', int(line['bbox'][3]))
            for seg in line['content']:
                for g in line.iter(self.tei_ns + 'g'):
                    el = SubElement(lel, 'charParams')
                    seg = g.xpath("ancestor::*[@type='segment']")
                    if seg and seg[0].get(self.xml_ns  + 'id') != last_seg_id:
                        el.set('wordStart', 'true')
                        last_seg_id = seg[0].get(self.xml_ns + 'id')
                    else:
                        el.set('wordStart', 'false')
                    el.text = ''.join(g.itertext())
                    if g.getparent().getparent().get('type') == 'grapheme':
                        el.set('l', g.getparent().getparent().get('ulx'))
                        el.set('t', g.getparent().getparent().get('uly'))
                        el.set('r', g.getparent().getparent().get('lrx'))
                        el.set('b', g.getparent().getparent().get('lry'))
                    cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                          tag='#' + g.get(self.xml_ns + 'id'))
                    if len(cert):
                       el.set('charConfidence', str(100.0 * float(cert[0].get('degree'))))
        fp.write(etree.tostring(page, xml_declaration=True, encoding='utf-8'))
        fp.flush()

    def write_alto(self, fp):
        """
        Writes the content of a TEI facsimile as an ALTO XML document.

        See [0] for further information and schemata. Output will conform to
        the version 3.0.

        Please note that the output will not be split into a series of
        "paragraphs" as segmentation algorithms don't produce them and they are
        dependent on typographic convention. Scores for alternatives are
        dropped as the standard does not provide for a way to encode them.
        Character confidences are rounded to the next lower confidence value
        (.98 -> 0, 0.05 -> 9).

        Args:
            fp (file): File descriptor to write to.

        [0] http://www.loc.gov/standards/alto/
        """
        alto = etree.Element('alto', xmlns="http://www.loc.gov/standards/alto/ns-v3#")
        desc = self.description

        description = SubElement(alto, 'Description')
        SubElement(description, 'MeasurementUnit').text = 'pixel'
        # use the image url as source image file name
        source_img = SubElement(description, 'sourceImageInformation')
        SubElement(source_img, 'fileName').text = desc[4]
        # convert responsibility statements to ocrProcessingSteps. As TEI
        # offers no way to distinguish between pre-, OCR, and postprocessing
        # for responsibility statements everything before a respStmt containing
        # 'recognition' is converted into preprocessing and everything after it
        # to postprocessing.
        ocr_proc = SubElement(description, 'OCRProcessing')
        mode = 'preProcessingStep'
        for id, respstmt in self.respstmt.iteritems():
            if 'recognition' in respstmt['resp'] and mode == 'preProcessingStep':
                mode = 'ocrProcessingStep'
            proc = SubElement(ocr_proc, mode)
            proc.set('ID', id)
            SubElement(proc, 'processingStepDescription').text = respstmt['resp']
            SubElement(proc, 'processingSoftware').text = respstmt['name']
            if mode == 'ocrProcessingStep':
                mode = 'postProcessingStep'

        layout = SubElement(alto, 'Layout')
        page = SubElement(layout, 'Page')
        page.set('HEIGHT', desc[3])
        page.set('WIDTH', desc[2])
        # why do all OCR formats insist on creating 'paragraph' containers? As
        # paragraphs are highly variable and dependent on typographic
        # conventions all text on the page is wrapped into a single paragraph.
        print_space = SubElement(page, 'PrintSpace')
        print_space.set('HPOS', 0.0)
        print_space.set('VPOS', 0.0)
        print_space.set('HEIGHT', desc[3])
        print_space.set('WIDTH', desc[2])
        text_block = SubElement(page, 'TextBlock')
        text_block.set('HPOS', 0.0)
        text_block.set('VPOS', 0.0)
        text_block.set('HEIGHT', desc[3])
        text_block.set('WIDTH', desc[2])
      
        for line in self.doc.iter(self.tei_ns + 'line'):
            text_line = SubElement(text_block, 'TextLine')
            text_line.set('HPOS', line.get('ulx'))
            text_line.set('VPOS', line.get('uly'))
            text_line.set('WIDTH', line.get('lrx') - line.get('ulx'))
            text_line.set('HEIGHT', line.get('lry') - line.get('uly'))
            text_line.set('ID', line.get(self.xml_ns + 'id'))

            # There are 3 cases of content beneath a line: a list of graphemes
            # (which are outright dumped into a SINGLE String element), some
            # segments (each is converted to a String or SP node depending on
            # content), or some corr node which are converted to String nodes
            # containing ALTERNATIVE nodes.
            for seg in line.xpath('child::node()'):
                if seg.get('type') == 'grapheme':
                    text = u''
                    certs = []
                    for g in line.iter(self.tei_ns + 'g'):
                        text += u''.join(g.itertext())
                        # confidences for graphemes are integers between 0 and
                        # 9 with 0 (wtf?) representing highest confidence
                        cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                              tag='#' + g.get(self.xml_ns + 'id'))
                        if cert:
                            certs.append(int(10 - 10 * float(cert[0].get('degree'))))
                    text_el = SubElement(text_line, 'String')
                    text_el.set('CONTENT', text)
                    text_el.set('CC', ' '.join(certs))
                    break
                elif seg.get('type') == 'segment':
                    text = ''.join(seg.itertext())
                    if text:
                        text_el = SubElement(text_line, 'String')
                        text_el.set('CONTENT', text)
                        # extract word confidences
                        w_cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                              tag='#' + seg.get(self.xml_ns + 'id'))
                        if w_cert:
                            text_el.set('WC', w_cert)
                        certs = []
                        # extract character confidences
                        for g in seg.iter(self.tei_ns + 'g'):
                            cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                                  tag='#' + g.get(self.xml_ns + 'id'))
                            if cert:
                                certs.append(int(10 - 10 * float(cert[0].get('degree'))))
                        if certs:
                            text_el.set('CC', ' '.join(certs))
                    else:
                        text_el = SubElement(text_line, 'SP')
                    text_el.set('HPOS', seg.get('ulx'))
                    text_el.set('VPOS', seg.get('uly'))
                    text_el.set('WIDTH', seg.get('lrx') - seg.get('ulx'))
                    text_el.set('HEIGHT', seg.get('lry') - seg.get('uly'))
                    text_el.set('ID', seg.get(self.xmls_ns + 'id'))
                elif seg.tag == self.tei_ns + 'choice':
                    sic = seg.find(self.tei_ns + 'sic')
                    orig_seg = sic.find('.//' + self.tei_ns + "zone[@type='segment']")
                    text = ''.join(orig_seg.itertext())
                    text_el = SubElement(text_line, 'String')
                    text_el.set('CONTENT', text)
                    # extract word confidences
                    w_cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                          tag='#' + orig_seg.get(self.xml_ns + 'id'))
                    if w_cert:
                        text_el.set('WC', w_cert)
                    certs = []
                    # extract character confidences
                    for g in orig_seg.iter(self.tei_ns + 'g'):
                        cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                              tag='#' + g.get(self.xml_ns + 'id'))
                        if cert:
                            certs.append(int(10 - 10 * float(cert[0].get('degree'))))
                    if certs:
                        text_el.set('CC', ' '.join(certs))
                    # extract segment alternatives
                    for corr in seg.iter(self.tei_ns + 'corr'):
                        SubElement(text_el, 'ALTERNATIVE').text = ''.join(corr.itertext())
                else:
                    raise NidabaTEIException('Unhandled input structure in ALTO conversion')
        fp.write(etree.tostring(page, pretty_print=True,
                 xml_declaration=True, encoding='utf-8'))
        fp.flush()

    def load_hocr(self, fp):
        pass

    def write_hocr(self, fp):
        pass

    def write_text(self, fp):
        """
        Writes the OCR record as plain text.

        Args:
            fp (file): File descriptor to write to.
        """
        for line in self.lines.itervalues():

            fp.write(line[-1].encode('utf-8').strip())
            fp.write('\n')
        fp.flush()


class TEIFacsimile(object):
    """
    A class encapsulating a TEI XML document following the TEI digital
    facsimile guidelines for embedded transcriptions.
    """

    xml_ns = '{http://www.w3.org/XML/1998/namespace}'
    tei_ns = '{http://www.tei-c.org/ns/1.0}'

    # automatically generated properties in the fileDesc element and xpath to their location

    fileDesc = ['titleStmt', 'editionStmt', 'publicationStmt', 'seriesStmt',
                'notesStmt', 'sourceDesc', ]

    def _generic_getter(self, field):
        el = self.doc.find('.//{0}teiHeader//{0}{1}{2}'.format(self.tei_ns,
                                                               self.fields[field][0],
                                                               self.fields[field][1]))
        if hasattr(el, 'text'):
            return el.text
        else:
            return None

    def _generic_setter(self, value, field):
        entry = self.fields[field]
        el = self.doc.find('.//{0}teiHeader//{0}{1}{2}'.format(self.tei_ns,
                                                               entry[0],
                                                               entry[1]))
        # create *Stmt in correct order
        parent = self.doc.find('.//{0}teiHeader//{0}{1}'.format(self.tei_ns, entry[0]))
        if parent is None:
            for loc in xrange(self.fileDesc.index(entry[0]), -1, -1):
                prev_stmt = self.doc.find('.//{0}{1}'.format(self.tei_ns, self.fileDesc[loc]))
                if prev_stmt is not None:
                    break
            parent = Element('{0}{1}'.format(self.tei_ns, entry[0]))
            prev_stmt.addnext(parent)
        # create all nodes along xpath in field[1]
        if el is None:
            el = parent
            for node in entry[1].split('/{')[1:]:
                el = SubElement(el, '{' + node)
        if isinstance(value, list):
            el.set(entry[2], value[1])
            value = value[0]
        el.text = value

    def __init__(self):
        doc = Element('TEI', nsmap={None: 'http://www.tei-c.org/ns/1.0'},
                      version='5.0')
        header = SubElement(doc, self.tei_ns + 'teiHeader')
        fileDesc = SubElement(header, self.tei_ns + 'fileDesc')
        SubElement(fileDesc, self.tei_ns + 'titleStmt')
        SubElement(fileDesc, self.tei_ns + 'publicationStmt')

        self.word_scope = None
        self.line_scope = None
        self.resp = None
        self.line_cnt = -1
        self.seg_cnt = -1
        self.grapheme_cnt = -1
        self.doc = doc

    def document(self, dim, image_url):
        sourceDoc = SubElement(self.doc, self.tei_ns + 'sourceDoc')
        surface = SubElement(sourceDoc, self.tei_ns + 'surface', ulx='0',
                             uly='0', lrx=str(dim[0]), lry=str(dim[1]))
        SubElement(surface, self.tei_ns + 'graphic', url=image_url)
        SubElement(surface, self.tei_ns + 'zone')

    @property
    def lang(self):
        """
        The language value of the teiHeader
        """
        el = self.doc.find('.//' + self.tei_ns + 'teiHeader')
        if el is not None:
            return el.get(self.xml_ns + 'lang')
        return None

    @lang.setter
    def lang(self, value):
        el = self.doc.find('.//' + self.tei_ns + 'teiHeader')
        el.set(self.xml_ns + 'lang', value)

    @property
    def description(self):
        """
        Returns a tuple containing a source document's path and its dimensions.
        """
        surface = self.doc.find('//{0}sourceDoc/{0}surface'.format(self.tei_ns))
        return (surface.get('ulx'),
                surface.get('uly'),
                surface.get('lrx'),
                surface.get('lry'),
                surface.find(self.tei_ns + 'graphic').get('url'))

    @property
    def respstmt(self):
        """
        Returns an ordered dictionary of responsibility statements from the XML
        document.
        """
        d = OrderedDict()
        for resp in self.doc.iter(self.tei_ns + 'respStmt'):
            rip = resp.get(self.xml_ns + 'id')
            d[rip] = {c.tag: c.text for c in resp.getchildren()}
        return d

    def add_respstmt(self, name, resp):
        """
        Adds a responsibility statement and treats all subsequently added text
        as a responsibility of this statement.

        Args:
            name (unicode): Identifier of the process that generated the
                            output.
            resp (unicode): Phrase describing the nature of the process
                            generating the output.

        Returns:
            A unicode string corresponding to the responsibility identifier.
        """
        id = -1
        for rstmt in self.doc.iter(self.tei_ns + 'respStmt'):
            id += 1
        r = SubElement(self.doc.find('.//' + self.tei_ns + 'titleStmt'),
                       self.tei_ns + 'respStmt')
        r.set(self.xml_ns + 'id', u'resp_' + unicode(id + 1))
        self.resp = r.get(self.xml_ns + 'id')
        SubElement(r, self.tei_ns + 'resp').text = resp
        SubElement(r, self.tei_ns + 'name').text = name
        return r.get(self.xml_ns + 'id')

    def scope_respstmt(self, id):
        """
        Scopes a respStmt for subsequent addition of graphemes/segments.

        Args:
            id (unicode): XML id of the responsibility statement

        Raises:
            NidabaTEIException if the identifier is unknown
        """
        if self.doc.find(".//{0}respStmt[@{1}id='{2}']".format(self.tei_ns,
                                                               self.xml_ns,
                                                               id)) is None:
            raise NidabaTEIException('No such responsibility statement.')
        self.resp = id

    @property
    def lines(self):
        """
        Returns an reading order sorted list of tuples in the format (x0, y0,
        x1, y1, xml id, text).
        """
        lines = []
        for line in self.doc.iter(self.tei_ns + 'line'):
            text = ''.join(line.itertext())
            lines.append((int(line.get('ulx')), int(line.get('uly')),
                          int(line.get('lrx')), int(line.get('lry')),
                          line.get(self.xml_ns + 'id'), text))
        return lines

    def add_line(self, dim):
        """
        Marks the beginning of a new topographical line and scopes it.

        Args:
            dim (tuple): A tuple containing the bounding box (x0, y0, x1, y1)
        """
        surface_zone = self.doc.find('.//{0}surface/{0}zone'.format(self.tei_ns))
        self.line_scope = SubElement(surface_zone, self.tei_ns + 'line',
                                     ulx=str(dim[0]), uly=str(dim[1]),
                                     lrx=str(dim[2]), lry=str(dim[3]))
        self.line_cnt += 1
        self.line_scope.set(self.xml_ns + 'id', 'line_' + str(self.line_cnt))
        if self.resp:
            self.line_scope.set('resp', '#' + self.resp)
        self.word_scope = None

    def scope_line(self, id):
        """
        Scopes a particular line for addition of segments/graphemes. Also
        disables the current segment scope.

        Args:
            id (unicode): XML id of the line tag

        Raises:
            NidabaTEIException if the identifier is unknown
        """
        line = self.doc.find(".//" + self.tei_ns + "line[@" + self.xml_ns +
                             "id='" + id + "']")
        if line is None:
            raise NidabaTEIException('No such line')
        self.line_scope = line

    @property
    def segments(self):
        """
        Returns an reading order sorted list of tuples in the format (x0, y0,
        x1, y1, confidence, id, text).
        """
        segments = []
        for seg in self.doc.iterfind('.//' + self.tei_ns + "zone[@type='segment']"):
            text = ''.join(seg.itertext())
            bbox = (int(seg.get('ulx')),
                    int(seg.get('uly')),
                    int(seg.get('lrx')),
                    int(seg.get('lry')))
            cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                  tag='#' + seg.get(self.xml_ns + 'id'))
            if len(cert):
                cert = int(100.0 * float(cert[0].get('degree')))
            else:
                cert = None
            segments.append(bbox + (cert,) + (seg.get(self.xml_ns + 'id'), text))
        return segments

    def add_segment(self, dim, lang=None, confidence=None):
        """
        Marks the beginning of a new topographical segment in the current
        scope. Most often this correspond to a word recognized by an engine.

        Args:
            dim (tuple): A tuple containing the bounding box (x0, y0, x1, y1)
            lang (unicode): Optional identifier of the segment language.
            confidence (float): Optional confidence value between 0 and 100.
        """
        zone = SubElement(self.line_scope, self.tei_ns + 'zone',
                          ulx=str(dim[0]), uly=str(dim[1]), lrx=str(dim[2]),
                          lry=str(dim[3]), type='segment')
        self.word_scope = zone
        self.seg_cnt += 1
        self.word_scope.set(self.xml_ns + 'id', 'seg_' + str(self.seg_cnt))
        if confidence:
            cert = SubElement(self.word_scope, self.tei_ns + 'certainty',
                              degree=u'{0:.2f}'.format(confidence / 100.0),
                              locus='value',
                              target='#' + 'seg_' + str(self.seg_cnt))
            if self.resp:
                cert.set('resp', '#' + self.resp)
        if self.resp:
            self.word_scope.set('resp', '#' + self.resp)

    def clear_segment(self):
        """
        Marks the end of the current topographical segment.
        """
        self.word_scope = None

    @property
    def graphemes(self):
        """
        Returns a reading order sorted list of tuples in the format (x0, y0,
        x1, y1, id, text).
        """
        graphemes = []
        for g in self.doc.iter(self.tei_ns + 'g'):
            text = ''.join(g.itertext())
            if g.getparent().getparent().get('type') == 'grapheme':
                bbox = (int(g.getparent().getparent().get('ulx')),
                        int(g.getparent().getparent().get('uly')),
                        int(g.getparent().getparent().get('lrx')),
                        int(g.getparent().getparent().get('lry')))
            else:
                bbox = (None, None, None, None)
            cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                  tag='#' + g.get(self.xml_ns + 'id'))
            if len(cert):
                cert = int(100.0 * float(cert[0].get('degree')))
            else:
                cert = None
            graphemes.append(bbox + (cert,) + (g.get(self.xml_ns + 'id'), text))
        return graphemes

    def add_graphemes(self, it):
        """
        Adds a number of graphemes to the current scope (either line or word).
        A line or segment has to be created beforehand.

        Args:
            it (iterable): An iterable returning a tuple containing a glyph
                           (unicode), and optionally the bounding box of this
                           glyph (x0, y0, x1, y1) and a recognition confidence
                           value in the range 0 and 100.
        """
        scope = self.word_scope if self.word_scope is not None else self.line_scope
        for t in it:
            conf = None
            if len(t) == 1:
                g = t
                zone = scope
            else:
                if len(t) == 2:
                    g, box = t
                else:
                    g, box, conf = t
                ulx, uly, lrx, lry = box
                zone = SubElement(scope, self.tei_ns + 'zone', ulx=str(ulx),
                                  uly=str(uly), lrx=str(lrx), lry=str(lry),
                                  type='grapheme', resp='#' + self.resp)
            # insert <seg> before <g> as TEI forbids a <g> directly beneath a
            # <zone>
            glyph = SubElement(SubElement(zone, self.tei_ns + 'seg'),
                               self.tei_ns + 'g')
            self.grapheme_cnt += 1
            glyph.set(self.xml_ns + 'id', 'grapheme_' + str(self.grapheme_cnt))
            glyph.text = g
            if conf:
                cert = SubElement(zone, self.tei_ns + 'certainty',
                                  degree=u'{0:.2f}'.format(conf / 100.0),
                                  locus='value',
                                  target='#' + 'grapheme_' +
                                  str(self.grapheme_cnt))
                if self.resp:
                    cert.set('resp', '#' + self.resp)
            if self.resp:
                glyph.set('resp', '#' + self.resp)

    def add_choices(self, id, it):
        """
        Adds alternative interpretations to an element.

        Args:
            id (unicode): Globally unique XML id of the element.
            it (iterable): An iterable returning a tuple containing an
                           alternative reading and an optional confidence value
                           in the range between 0 and 100.
        """
        el = self.doc.xpath("//*[@xml:id=$tagid]", tagid=id)[0]
        # remove old tree only if not already part of an choice segment.
        parent = el.getparent()
        if parent.tag == self.tei_ns + 'sic':
            choice = parent.find('..')
        else:
            sic = deepcopy(el)
            idx = parent.index(el)
            parent.remove(el)
            choice = Element(self.tei_ns + 'choice')
            parent.insert(idx, choice)
            # reinsert beneath sic element
            SubElement(choice, self.tei_ns + 'sic').append(sic)
        for alt in it:
            corr = SubElement(choice, self.tei_ns + 'corr')
            if self.resp:
                corr.set('resp', '#' + self.resp)
            corr.text = alt[0]
            if len(alt) == 2:
                cert = SubElement(corr, self.tei_ns + 'certainty',
                                  degree=u'{0:.2f}'.format(alt[1] / 100.0),
                                  locus='value')
                if self.resp:
                    cert.set('resp', '#' + self.resp)

    def clear_lines(self):
        """
        Deletes all <line> nodes from the document.
        """
        for zone in self.doc.iterfind('.//' + self.tei_ns +
                                      "line"):
            zone.getparent().remove(zone)
        self.line_scope = None
        self.word_scope = None
        self.line_cnt = -1
        self.seg_cnt = -1
        self.grapheme_cnt = -1

    def clear_graphemes(self):
        """
        Deletes all grapheme zone nodes from the document. Mainly used when
        combining page segmentation algorithms extracting graphemes and OCR
        engines operating on lexemes. Also resets the current scope to the
        first line (and if applicable its first segment).
        """
        for zone in self.doc.iterfind('.//' + self.tei_ns +
                                      "zone[@type='grapheme']"):
            zone.getparent().remove(zone)
        self.line_scope = self.doc.find('.//' + self.tei_ns + 'line')
        self.word_scope = self.doc.find('.//' + self.tei_ns + "zone[@type='segment']")
        self.grapheme_cnt = -1

    def clear_segments(self):
        """
        Deletes all word zone nodes from the document. Mainly used when
        combining page segmentation algorithms extracting lexemes (and
        graphemes) and OCR engines operating on lines. Also resets the current
        scope to the first line.
        """
        for zone in self.doc.iterfind('.//' + self.tei_ns +
                                      "zone[@type='segment']"):
            zone.getparent().remove(zone)
        self.line_scope = self.doc.find('.//' + self.tei_ns + 'line')
        self.word_scope = None
        self.seg_cnt = -1
        self.grapheme_cnt = -1

    def load_hocr(self, fp):
        """
        Extracts as much information as possible from an hOCR file and converts
        it to TEI.

        TODO: Write a robust XSL transformation.

        Args:
            fp (file): File descriptor to read data from.
        """
        doc = etree.HTML(fp.read())
        self.clear_lines()
        self.clear_segments()
        self.clear_graphemes()
        el = doc.find(".//meta[@name='ocr-system']")
        if el is not None:
            self.add_respstmt(el.get('content'), 'ocr-system')
        page = doc.find('.//div[@class="ocr_page"]')
        o = _parse_hocr(page.get('title'))
        self.document(o['bbox'], o['image'][0])
        for line in doc.iterfind('.//span[@class="ocr_line"]'):
            self.add_line(_parse_hocr(line.get('title'))['bbox'])
            if not line.xpath('.//span[starts-with(@class, "ocrx")]'):
                self.add_graphemes(''.join(line.itertext()))
            for span in line.xpath('.//span[starts-with(@class, "ocrx")]'):
                o = _parse_hocr(span.get('title'))
                confidence = None
                bbox = None
                if 'bbox' in o:
                    bbox = o['bbox']
                if 'x_wconf' in o:
                    confidence = int(o['x_wconf'][0])
                self.add_segment(bbox, confidence=confidence)
                self.add_graphemes(''.join(span.itertext()))
                if span.tail:
                    self.clear_segment()
                    # strip trailing whitespace as some engines add it
                    # arbitrarily or for formatting purposes
                    self.add_graphemes(span.tail.rstrip())

    def write_hocr(self, fp):
        """
        Writes the TEI document as an hOCR file.

        Args:
            fp (file): File descriptor to write to.
        """
        page = etree.Element('html', xmlns="http://www.w3.org/1999/xhtml")
        head = SubElement(page, 'head')
        SubElement(head, 'title').text = self.title
        SubElement(head, 'meta', name="ocr-system",
                   content=self.respstmt.values()[-1][self.tei_ns + 'name'])
        capa = "ocr_page"
        if self.lines is not None:
            capa += ", ocr_line"
        if self.segments is not None:
            capa += ", ocrx_word"
        SubElement(head, 'meta', name='ocr-capabilities', content=capa)
        body = SubElement(page, 'body')
        ocr_page = SubElement(body, 'div', title='')
        ocr_page.set('class', 'ocr_page')
        for line in self.doc.iter(self.tei_ns + 'line'):
            ocr_line = SubElement(ocr_page, 'span')
            ocr_line.set('class', 'ocr_line')
            ocr_line.set('title', 'bbox ' + ' '.join([str(line.get('ulx')),
                                                      str(line.get('uly')),
                                                      str(line.get('lrx')),
                                                      str(line.get('lry'))]))
            # get text not in word segments interleaved with segments
            ocrx_word = None
            for seg in line.xpath('child::node()'):
                if ocrx_word is not None:
                    ocrx_word.text += ' '
                if isinstance(seg, etree._ElementStringResult):
                    if ocr_line.text is None:
                        ocr_line.text = ''
                    ocr_line.text += seg
                else:
                    # zone from
                    ocrx_word = SubElement(ocr_line, 'span')
                    ocrx_word.set('class', 'ocrx_word')
                    title = 'bbox ' + ' '.join([str(seg.get('ulx')),
                                               str(seg.get('uly')),
                                               str(seg.get('lrx')),
                                               str(seg.get('lry'))])
                    cert = seg.find('.//{0}certainty'.format(self.tei_ns))
                    if cert is not None:
                        title += '; x_wconf ' + str(int(100.0 *
                                                    float(cert.get('degree'))))
                    ocrx_word.set('title', title)
                    ocrx_word.text = ''.join(seg.itertext())
            SubElement(ocr_page, 'br')
        fp.write(etree.tostring(page, pretty_print=True,
                 doctype='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 '
                         'Transitional//EN" '
                         '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
                 xml_declaration=True, encoding='utf-8'))
        fp.flush()

    def write_abbyyxml(self, fp):
        """
        Writes the TEI document in a format reminiscent of Abbyy FineReader's
        XML output. Its basic format is:

        <text>
        <line l="0" r="111" t="6" b="89">
        <charParams l="0" r="78" t="6" b="89" charConfidence="76" wordStart="true">D</charParams>
        <charParams l="86" r="111" t="24" b="89" charConfidence="76" wordStart="false">e</charParams>
        </line>
        ....
        </text>

        Please note that alternative readings as produced for example by spell
        checking are dropped from the output. 

        Args:
            fp (file): File descriptor to write to.
        """
        page = etree.Element('document')
        p = etree.SubElement(page, 'page')
        surface = self.doc.find('.//{0}sourceDoc/{0}surface'.format(self.tei_ns))
        p.set('width', surface.get('lrx'))
        p.set('height', surface.get('lry'))
        p.set('originalCoords', '1')
        text = etree.SubElement(p, 'text')
        last_seg_id = None
        for line in self.doc.iter(self.tei_ns + 'line'):
            lel = SubElement(text, 'line')
            lel.set('l', line.get('ulx'))
            lel.set('t', line.get('uly'))
            lel.set('r', line.get('lrx'))
            lel.set('b', line.get('lry'))
            for g in line.iter(self.tei_ns + 'g'):
                el = SubElement(lel, 'charParams')
                seg = g.xpath("ancestor::*[@type='segment']")
                if seg and seg[0].get(self.xml_ns  + 'id') != last_seg_id:
                    el.set('wordStart', 'true')
                    last_seg_id = seg[0].get(self.xml_ns + 'id')
                else:
                    el.set('wordStart', 'false')
                el.text = ''.join(g.itertext())
                if g.getparent().getparent().get('type') == 'grapheme':
                    el.set('l', g.getparent().getparent().get('ulx'))
                    el.set('t', g.getparent().getparent().get('uly'))
                    el.set('r', g.getparent().getparent().get('lrx'))
                    el.set('b', g.getparent().getparent().get('lry'))
                cert = self.doc.xpath("//*[local-name()='certainty' and @target=$tag]",
                                      tag='#' + g.get(self.xml_ns + 'id'))
                if len(cert):
                   el.set('charConfidence', str(100.0 * float(cert[0].get('degree'))))
        fp.write(etree.tostring(page, xml_declaration=True, encoding='utf-8'))
        fp.flush()

    def write_text(self, fp):
        """
        Writes the TEI document as plain text.

        Args:
            fp (file): File descriptor to write to.
        """
        for line in self.lines:
            fp.write(line[-1].encode('utf-8').strip())
            fp.write('\n')
        fp.flush()

    def write(self, fp):
        """
        Writes the TEI XML document to a file object.

        Args:
            fp (file): file object to write to
        """
        fp.write(etree.tostring(self.doc, xml_declaration=True, pretty_print=True,
                                encoding='utf-8'))
        fp.flush()

    def read(self, fp):
        """
        Reads an XML document from a file object and populates all recognized
        attributes. Also sets the scope to the first line (and if applicable
        segment) of the document.

        Args:
            fp (file): file object to read from
        """
        self.doc = etree.parse(fp).getroot()
        self.line_cnt = len(list(self.doc.iter(self.tei_ns + 'line'))) - 1
        self.seg_cnt = len(list(self.doc.iterfind('.//' + self.tei_ns + "zone[@type='segment']"))) - 1
        self.grapheme_cnt = len(list(self.doc.iter(self.tei_ns + 'g'))) - 1


# populate properties on the class. Note that it operates on the TEIFacsimile
# class itself.
for field in TEIFacsimile.fields:
    setattr(TEIFacsimile, field, property(partial(TEIFacsimile._generic_getter,
            field=field), partial(TEIFacsimile._generic_setter, field=field)))

for field in OCRRecord.fields:
    setattr(OCRRecord, field, property(partial(OCRRecord._generic_getter,
            field=field), partial(OCRRecord._generic_setter, field=field)))
