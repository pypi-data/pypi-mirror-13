import pytest
import click
import re

from click.testing import CliRunner
from pelican_do.main import main

import pelican_do.post


def test_post_command_help():
    runner = CliRunner()
    result = runner.invoke(main, ['post', '--help'])
    assert re.search('Usage: .* post \[OPTIONS\] NAME', result.output)


def test_post_command_help(monkeypatch):
    def mockreturn(today, name, format, title, category, authors, tags, summary):

        assert name == 'a post name'
        assert format == 'rst'
        assert title == 'some title'
        assert category == 'some category'
        assert authors == ('Mosca', 'Smith')
        assert tags == ('first tag', 'second tag')
        assert summary == 'a summary'

        return True

    monkeypatch.setattr(pelican_do.post, 'post', mockreturn)

    runner = CliRunner()

    result = runner.invoke(main, ['post', 'a post name', '--format', 'rst', '--title',
                                  'some title', '--category', 'some category', '--authors',
                                  'Mosca', '--authors', 'Smith', '--tags', 'first tag', '--tags', 'second tag',
                                  '--summary', 'a summary'])
    assert not result.exception

    print 'Output: %s' % result.output
    assert True
    # assert re.search('Usage: .* post \[OPTIONS\] NAME', result.output)


#   with runner.isolated_filesystem():
#     with open('hello.txt', 'w') as f:
#         f.write('Hello World!')

#     result = runner.invoke(main, ['post', '--help'])
#     Usage: pelican-do post [OPTIONS] NAME
#     assert result.exit_code == 0
#     assert result.output == 'Hello World!\n'
# #
