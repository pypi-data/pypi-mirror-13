# -*- coding: utf-8 -*-
import fnmatch
import imp
import os
import re
import sys

import click
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def render_template(jinja_template, extra_variables):
    print '    BASE TEMPLATE:', jinja_template
    print '    EXTRA VARS   :', extra_variables

    environment = Environment(loader=FileSystemLoader([os.path.dirname(jinja_template)]), trim_blocks=True, lstrip_blocks=True)
    environment.undefined = StrictUndefined
    template = environment.get_template(os.path.basename(jinja_template))
    return template.render(extra_variables)


def main(path, settings=None):
    extra_variables = {}
    ignore_jinja_templates = []
    if settings:
        extra_variables = getattr(settings, 'EXTRA_VARIABLES', {})
        ignore_jinja_templates = getattr(settings, 'IGNORE_JINJA_TEMPLATES', [])

    if os.path.isdir(path):
        jinja_templates = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.jinja*'):
                jinja_templates.append(os.path.join(root, filename))
    else:
        jinja_templates = [path, ]  # path is just a file, actually

    for jinja_template in jinja_templates:
        skip = False
        for jinja_template_to_be_ignored in ignore_jinja_templates:
            if re.match(jinja_template_to_be_ignored, jinja_template):
                print 'SKIPPING:', jinja_template
                skip = True
                break

        if skip:
            continue

        html_template, _ = os.path.splitext(jinja_template)
        html_template = '{}.html'.format(html_template)

        print 'CREATING:', html_template
        try:
            with open(html_template, 'w') as f:
                f.write(render_template(jinja_template, extra_variables=extra_variables).encode('utf-8'))
        except:
            os.unlink(html_template)
            raise

    print 'DONE!  =]'


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--settings', default=None, help='Settings file to use.')
def main_command(path, settings=None):
    current_dir = os.getcwd()

    if settings:
        settings_file = os.path.join(current_dir, settings)
        if not os.path.exists(settings_file):
            raise IOError(u'Settings file not found: {}'.format(settings_file))

        sys.path.insert(0, '')
        settings = imp.load_source(current_dir, settings)

    current_dir = os.path.join(current_dir, path)
    main(settings=settings, path=current_dir)
