# -*- coding: utf-8 -*-
# Copyright (c) Polyconseil SAS. All rights reserved.

from __future__ import unicode_literals

from io import BytesIO, StringIO
import logging

from dokang.harvesters.base import Harvester

try:
    from pdfminer import pdfpage
    del pdfpage
    HAS_PDFMINER_3K = False
except ImportError:
    HAS_PDFMINER_3K = True

from pdfminer.pdftypes import PDFObjRef


logger = logging.getLogger('dokang')

# Code has been lifted from various parts of PDFMiner. Really, I don't
# know what I am doing... We read the file twice (once for the title,
# once for the content), there must be a better way to do all this. In
# the meantime, it works well enough for our modest set of PDF files.

# The API has changed between pdfminer and pdfminer3k.
if HAS_PDFMINER_3K:
    from pdfminer.converter import TextConverter
    from pdfminer.pdfinterp import PDFResourceManager, process_pdf
    from pdfminer.pdfparser import PDFDocument, PDFParser

    def extract_content(fp, encoding):
        content = StringIO()  # not BytesIO
        rsrcmgr = PDFResourceManager(caching=True)
        device = TextConverter(rsrcmgr, content)
        pagenos = set()
        process_pdf(rsrcmgr, device, fp, pagenos)
        device.close()
        content.seek(0)
        return content.getvalue().encode('utf-8')
else:
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    def extract_content(fp, encoding):
        content = BytesIO()
        rsrcmgr = PDFResourceManager(caching=True)
        device = TextConverter(
            rsrcmgr, content, codec=encoding, laparams=LAParams(), imagewriter=None)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp):
            interpreter.process_page(page)
        device.close()
        content.seek(0)
        return content.getvalue()


class PdfHarvester(Harvester):
    """Harvest content from a PDF."""

    def harvest_file(self, path):
        with open(path, 'rb') as fp:
            # FIXME: how do we know which encoding to use? Should we
            # use 'chardet' to detect it?
            encoding = 'utf-8'
            parser = PDFParser(fp)
            if HAS_PDFMINER_3K:
                doc = PDFDocument()
                parser.set_document(doc)
                doc.set_parser(parser)
            else:
                doc = PDFDocument(parser)
            title = doc.info[0].get('Title', '')
            if isinstance(title, PDFObjRef):
                title = title.resolve()
            if isinstance(title, bytes):
                # This may not be necessary with pdfminer3k.
                try:
                    title = title.decode(encoding)
                except UnicodeDecodeError:
                    logger.warning('Could not correctly decode title of "%s".', path)
                    title = title.decode(encoding, 'ignore')
            fp.seek(0)
            content = extract_content(fp, encoding).strip()
            try:
                content = content.decode(encoding)
            except UnicodeDecodeError:
                logger.warning('Could not correctly decode content of "%s".', path)
                content = content.decode(encoding, 'ignore')
        return {
            'title': title,
            'content': content,
            'kind': 'PDF',
        }
