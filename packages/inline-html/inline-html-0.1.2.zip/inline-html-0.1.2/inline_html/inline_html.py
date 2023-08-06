
from __future__ import print_function
import os
import uuid
import base64
import click
import cssutils
import mimetypes
import lxml.html


def resource_to_data(path, in_file):
    """Convert a file (specified by a path) into a data URI."""

    if path.startswith(('data:', 'http')):
        return path
    path = os.path.join(os.path.dirname(in_file), path)
    if not os.path.exists(path):
        raise IOError(path)
    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as fp:
        data = fp.read()
        data64 = b''.join(base64.encodestring(data).splitlines())
        return 'data:%s;base64,%s' % (mime, data64.decode('ascii'))


@click.command()
@click.option('--in-file', default='', help='source HTML file')
@click.option('--out-file', default='out.html', help='output HTML file')
def inline_resources(in_file, out_file):

    if not in_file or not os.path.exists(in_file):
        raise IOError('No input file given or input file does not exist')

    with open(in_file, 'rb') as fp:
        html = fp.read()

    root = lxml.html.fromstring(html)

    # convert all images to data-uri
    for img in root.xpath('//img'):
        src = img.attrib['src']
        data = resource_to_data(src, in_file)
        img.attrib['src'] = data

    # inline all external stylesheets and replace url()
    # references with data-uri
    for link in root.xpath('//link'):
        href = link.attrib['href']
        if not href.startswith(('data:', 'http')):
            href = os.path.join(os.path.dirname(in_file), href)
        with open(href, 'rb') as fp:
            css = fp.read()
        css_hashes = dict()  # hash to data-uri
        sheet = cssutils.parseString(css)
        for rule in sheet:
            for k in rule.style.keys():
                v = rule.style[k]
                # replace url(...) with a hash (since cssutils) does
                # not play well with data-uri
                if v.startswith('url('):
                    lpos = v.find('(')
                    rpos = v.find(')')
                    data = resource_to_data(v[lpos + 1 : rpos], in_file)
                    suffix = v [rpos + 1 : ]
                    css_hash = str(uuid.uuid4())
                    rule.style[k] = css_hash
                    css_hashes[css_hash] = 'url({}) {}'.format(data, suffix)
    
        # replace hashes with data-uri
        css = sheet.cssText
        for css_hash in css_hashes:
            css = css.replace(
                css_hash.encode('ascii'), css_hashes[css_hash].encode('ascii'))

        # replace <link> with inlined <style>
        node = lxml.etree.Element('style')
        node.attrib['type'] = 'text/css'
        node.text = css
        link.getparent().replace(link, node)

    with open(out_file, 'wb') as fp:
        fp.write(lxml.html.tostring(root))

    print('Output written to {}'.format(out_file))

if __name__ == '__main__':
    inline_resources()


