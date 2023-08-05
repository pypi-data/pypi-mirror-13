from jinja2 import Environment

import datetime
import textwrap

from pelican_do.utils.filters import *
import slugify

import os
import errno

class PostError(Exception):
    pass

templates = {
  'rst': textwrap.dedent('''
    {{title|rst_title}}
    :date: {{date|pelican_datetime}}
    {% if tags %}
    :tags: {{tags|join(', ')}}
    {% endif %}
    :category: {{category}}
    :slug: {{slug}}
    {% if authors %}
    :authors: {{authors|join(', ')}}
    {% endif %}
    {% if summary %}
    :summary: {{summary}}
    {% endif %}
  '''),

  'md': textwrap.dedent('''
    Title: {{title}}
    Date: {{date|pelican_datetime}}
    Category: {{category}}
    {% if tags %}
    Tags: {{tags|join(', ')}}
    {% endif %}
    Slug: {{slug}}
    {% if authors %}
    Authors: {{authors|join(', ')}}
    {% endif %}
    {% if summary %}
    Summary: {{summary}}
    {% endif %}

    This is the content of my super blog post.
  ''')
}

def post(today, name, format, title, category, authors, tags, summary):

  if not os.path.isfile('pelicanconf.py'):
    raise PostError('"pelicanconf.py" must exist in current directory')

  if not os.path.isdir('content'):
    raise PostError('"content" directory does not exist')

  title = title or name

  jinja_environment = Environment()
  jinja_environment.filters['rst_title'] = rst_title
  jinja_environment.filters['pelican_datetime'] = pelican_datetime

  template = jinja_environment.from_string(templates[format])
#
  slug = slugify.slugify(title, to_lower=True)

  filename = '%s-%s.%s' % (today.strftime('%Y-%m-%d'), slugify.slugify(name, to_lower=True), format)

  article_path = os.path.join('content', category)

  try:
    os.makedirs(article_path)

  except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise

  with open(os.path.join(article_path, filename), 'w') as f:
    f.write(template.render(
      title=title,
      date=today,
      tags=tags,
      slug=slug,
      category=category,
      summary=summary,
      authors=authors))

