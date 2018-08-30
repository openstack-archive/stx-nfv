#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# The following installs are required:
#   pip install pyyaml
#   pip install jinja2
#
import os
import six
import yaml
import shutil
import pprint
import argparse
from jinja2 import Environment, FileSystemLoader


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_SRC_DIR = CURRENT_DIR + '/documentation'
HTML_SRC_DIR = CURRENT_DIR + '/html_layout'


def build_html_doc(build_dir, document_data):
    """
    Build HTML Documentation
    """
    shutil.copytree(HTML_SRC_DIR + '/css', build_dir + '/css')
    shutil.copytree(HTML_SRC_DIR + '/images', build_dir + '/images')
    shutil.copytree(HTML_SRC_DIR + '/javascript', build_dir + '/javascript')

    j2_env = Environment(loader=FileSystemLoader(HTML_SRC_DIR + '/templates'),
                         trim_blocks=True)

    index_template = j2_env.get_template('index.html')
    index_html = index_template.render(document_data)

    with open(build_dir + '/index.html', "w") as f:
        six.print_(index_html, file=f)

        for toc_entry in document_data['table_of_contents']:
            toc_entry_data = yaml.load(open(DOC_SRC_DIR + '/' +
                                            toc_entry['link'] +
                                            '.yaml'))
            toc_entry_data['page_link'] = toc_entry['link']

            page_content_template = j2_env.get_template('page_content.html')
            toc_entry_html = page_content_template.render(toc_entry_data)
            six.print_(toc_entry_html, file=f)


if __name__ == '__main__':
    """
    Document Builder
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--builder', help='type of build')
    parser.add_argument('build_dir', help='build directory')
    args = parser.parse_args()

    if not os.path.exists(args.build_dir):
        os.makedirs(args.build_dir)

    document_data = yaml.load(open(DOC_SRC_DIR + '/document.yaml'))

    if 'html' == args.builder:
        build_html_doc(args.build_dir, document_data)
    else:
        print("No builder selected, do nothing.")
