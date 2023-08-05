import click
import datetime

import pelican_do.post

@click.group()
def main():
  pass

@main.command()
@click.argument('name')
@click.option('--format', default='rst', type=click.Choice(['rst', 'md']), help='Format used to write the article.')
@click.option('--title', type=str, help='Title for the article. By default, it will be the name.', default=None)
@click.option('--category', type=str, help='category for the article.', default=None)
@click.option('--tags', '-t', multiple=True, type=str, default=None, help='Tags for the article.')
@click.option('--summary', type=str, help='Summary for the article.', default=None)
def post(name, format, title, category, tags, summary):
  today = datetime.datetime.now()
  pelican_do.post.post(today, name, format, title, category, tags, summary)

if __name__ == '__main__':
  main()
