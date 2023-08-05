import unittest
import datetime
import os.path
import os
import tempfile
import shutil

from pelican_do.post import post, PostError

def create_empty_config():
  open('pelicanconf.py', 'a').close()

class PostTest(unittest.TestCase):
  def setUp(self):
    self.cwd = tempfile.mkdtemp()
    os.chdir(self.cwd)

  def tearDown(self):
    shutil.rmtree(self.cwd)
    self.cwd = None

class PostNoConfigError(PostTest):
  def shortDescription(self):
    return 'Post action must throw an exception if no "pelicanconf.py" file exists in current directory'

  def test(self):
    os.mkdir('content')

    today = datetime.datetime(2012, 9, 16, 23, 12, 11)
    name = 'a post name'
    format = 'rst'
    category = 'new category'
    tags = ['tag1', 'tag2']
    authors = [ 'joe smith', 'Juan Carlos Batman']
    summary = 'This is a summary'
    title = 'a title'

    self.assertRaises(PostError, post, today, name, format, title, category, authors, tags, summary)


class PostNoContentError(PostTest):
  def shortDescription(self):
    return 'Post action must throw an exception if no content directory exist'

  def test(self):
    create_empty_config()

    today = datetime.datetime(2012, 9, 16, 23, 12, 11)
    name = 'a post name'
    format = 'rst'
    category = 'new category'
    tags = ['tag1', 'tag2']
    authors = [ 'joe smith', 'Juan Carlos Batman']
    summary = 'This is a summary'
    title = 'a title'

    self.assertRaises(PostError, post, today, name, format, title, category, authors, tags, summary)

class PostRstTest(PostTest):
  def shortDescription(self):
    return 'Create a post with filename based on post name slug and date and RST with metadata'

  def test(self):
    create_empty_config()
    os.mkdir('content')

    today = datetime.datetime(2012, 9, 16, 23, 12, 11)
    name = 'a post name'
    format = 'rst'
    category = 'new category'
    tags = ['tag1', 'tag2']
    authors = [ 'joe smith', 'Juan Carlos Batman']
    summary = 'This is a summary'
    title = 'a title'

    post(today, name, format, title, category, authors, tags, summary)

    content_dir = os.path.join(self.cwd, 'content', category)
    article_path = os.path.join(content_dir, '2012-09-16-a-post-name.rst')

    self.assertTrue(os.path.isdir(content_dir))
    self.assertTrue(os.path.isfile(article_path))

    with open(article_path, 'r') as f:
      content = f.read()

      # title
      self.assertTrue(
        'a title\n#######\n' in content
      )

      self.assertTrue(
        ':category: new category\n' in content
      )

      self.assertTrue(
        ':date: 2012-09-16 23:12\n' in content
      )

      self.assertTrue(
        ':tags: tag1, tag2\n' in content
      )

      self.assertTrue(
        ':authors: joe smith, Juan Carlos Batman\n' in content
      )

      self.assertTrue(
        ':summary: This is a summary\n' in content
      )

class PostRstDefaultTest(PostTest):
  def shortDescription(self):
    return 'Create a post with filename based on post name slug and date and RST with default metadata'

  def test(self):
    create_empty_config()
    os.mkdir('content')


    today = datetime.datetime(2015, 12, 1, 3, 1, 21)
    name = 'Post name With defaults'
    format = 'rst'
    category = 'a category'
    tags = None
    authors = None
    summary = None
    title = 'This is a title'

    post(today, name, format, title, category, authors, tags, summary)

    content_dir = os.path.join(self.cwd, 'content', category)
    article_path = os.path.join(content_dir, '2015-12-01-post-name-with-defaults.rst')

    self.assertTrue(os.path.isdir(content_dir))
    self.assertTrue(os.path.isfile(article_path))

    with open(article_path, 'r') as f:
      content = f.read()

      # title
      self.assertTrue(
        'This is a title\n###############\n\n' in content
      )

      self.assertTrue(
        ':date: 2015-12-01 03:01\n' in content
      )

      self.assertTrue(
        ':tags:' not in content
      )

      self.assertTrue(
        ':authors:' not in content
      )

      self.assertTrue(
        ':summary:' not in content
      )



class PostMdTest(PostTest):
  def shortDescription(self):
    return 'Create a post with filename based on post name slug and date and Markdown with metadata'

  def test(self):
    create_empty_config()
    os.mkdir('content')

    today = datetime.datetime(2012, 9, 16, 23, 12, 11)
    name = 'a post name'
    format = 'md'
    category = 'new category'
    tags = ['tag1', 'tag2']
    authors = [ 'joe smith', 'Juan Carlos Batman']
    summary = 'This is a summary'
    title = 'a title'

    post(today, name, format, title, category, authors, tags, summary)

    content_dir = os.path.join(self.cwd, 'content', category)
    article_path = os.path.join(content_dir, '2012-09-16-a-post-name.md')

    self.assertTrue(os.path.isdir(content_dir))
    self.assertTrue(os.path.isfile(article_path))

    with open(article_path, 'r') as f:
      content = f.read()

      # title
      self.assertTrue(
        'Title: a title\n' in content
      )

      self.assertTrue(
        'Category: new category\n' in content
      )

      self.assertTrue(
        'Date: 2012-09-16 23:12\n' in content
      )

      self.assertTrue(
        'Tags: tag1, tag2\n' in content
      )

      self.assertTrue(
        'Authors: joe smith, Juan Carlos Batman\n' in content
      )

      self.assertTrue(
        'Summary: This is a summary\n' in content
      )
class PostMdDefaultTest(PostTest):
  def shortDescription(self):
    return 'Create a post with filename based on post name slug and date and Markdown with default metadata'

  def test(self):
    create_empty_config()
    os.mkdir('content')

    today = datetime.datetime(2015, 12, 1, 3, 1, 21)
    name = 'Post name With defaults'
    format = 'md'
    category = 'a category'
    tags = None
    authors = None
    summary = None
    title = 'This is a title'

    post(today, name, format, title, category, authors, tags, summary)

    content_dir = os.path.join(self.cwd, 'content', category)
    article_path = os.path.join(content_dir, '2015-12-01-post-name-with-defaults.md')

    self.assertTrue(os.path.isdir(content_dir))
    self.assertTrue(os.path.isfile(article_path))

    with open(article_path, 'r') as f:
      content = f.read()

      # title
      self.assertTrue(
        'Title: This is a title\n' in content
      )

      self.assertTrue(
        'Date: 2015-12-01 03:01\n' in content
      )

      self.assertTrue(
        'Category: a category' in content
      )

      self.assertTrue(
        'Authors:' not in content
      )

      self.assertTrue(
        'Summary:' not in content
      )


