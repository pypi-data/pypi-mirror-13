# coding: utf-8

"""
cat
~~~~
                                    \/
a static blog generator for -[c]a[t][0.]
                               |   |

Usage:

    $ ca init:          generate a cat blog

    $ ca new <example>: add a new blog post(example.md)
      \_title:          -- post title
      \_category:       -- category
      \_tag:            -- tag

    $ python blog.py    -- run the blog on localhost

    $ ca upload:        deploy your blog(use github)

    $ ca upgrade <theme>:       upgrade the blog theme

Options:

    $ ca --help:        show the help message

Install:

    $ pip install cat (--upgrade)

"""

import os
import sys
import shutil

# operators
from operators import _mkdir_p
from operators import init_code

# templates
from ..server.blog import init_blog_code
from ..server.config import init_config_code

# pages
from ..pages.hello import init_hello_code

# logging
import logging
from logging import StreamHandler, DEBUG

# logger
logger = logging.getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

# log
def run_in_root(path):
    """
    make sure all the cli run under blog root path
    """
    if path.split('/')[-1] != 'blog':
        logger.warning(
            '''
            \033[31m{warning}\033[0m
            ==> please run the command under blog folder!
            '''
        )
        exit(1)
    else:
        pass


def warning_post_exist(postname, dirpath):
    """
    ca new <postname>
    warning if postname already in pages/
    """
    if '%s.md' % postname in os.listdir(dirpath):
        logger.warning(
            '''
            \033[31m{warning}\033[0m
            ==> post %s already exist! please change the name
            ==> and try again !
            ''' % postname
        )
        exit(1)
    else:
        pass

def start_init(abspath):
    """
    info for start init
    """
    logger.info(
        '''
        \033[33m{info}\033[0m
        ==> start init your cat blog
        ==> blog path: \033[32m%s\033[0m
        ''' % abspath
    )

def init_done():
    """
    info for init done
    """
    logger.info(
        '''
        \033[33m{info}\033[0m
        ==> init your cat blog, done!
        '''
    )


# click
import click

@click.group()
def cli():
    pass


@click.command()
def init():
    """
    ca init: generate a cat blog
    """
    project_path = os.path.join(os.getcwd(), 'blog')

    start_init(project_path)
    _mkdir_p(project_path)

    # init server
    os.chdir(project_path)
    init_code('blog.py', init_blog_code)
    init_code('config.py', init_config_code)

    # init pages
    pages_path = os.path.join(project_path, 'pages')
    _mkdir_p(pages_path)
    os.chdir(pages_path)
    init_code('hello-cat.md', init_hello_code)

    # init theme(default theme is cat)
    theme_path = os.path.join(project_path, 'theme')
    _mkdir_p(theme_path)
    os.chdir(theme_path)
    # clone theme(default is cat)
    os.popen('git clone https://github.com/neo1218/cat-theme-cat.git cat')
    cat_path = os.path.join(theme_path, 'cat')
    templates_path = os.path.join(cat_path, 'templates')
    static_path = os.path.join(cat_path, 'static')
    templates_target_path = os.path.join(project_path, 'templates')
    static_target_path = os.path.join(project_path, 'static')
    # copy tree
    shutil.copytree(templates_path, templates_target_path)
    shutil.copytree(static_path, static_target_path)

    init_done()


@click.command()
@click.argument('theme')
def upgrade(theme):
    """
    upgrade the theme
    """
    run_in_root(os.getcwd())
    theme_path = os.path.join(os.getcwd(), 'theme/%s' % theme)
    templates_path = os.path.join(theme_path, 'templates')
    templates_target_path = os.path.join(os.getcwd(), 'templates')
    static_path = os.path.join(theme_path, 'static')
    static_target_path = os.path.join(os.getcwd(), 'static')

    shutil.rmtree(templates_target_path)
    shutil.rmtree(static_target_path)
    shutil.copytree(templates_path, templates_target_path)
    shutil.copytree(static_path, static_target_path)

    logger.info('''
        \033[33m{info}\033[0m
        ==> upgrade the theme!
        '''
    )


@click.command()
@click.argument('post')
def new(post):
    """
    add a new blog post
    """
    run_in_root(os.getcwd())
    pages_path = os.path.join(os.getcwd(), 'pages')
    warning_post_exist(post, pages_path)

    title = click.prompt('\_title ')
    date = click.prompt('\_date[YYYY-MM-DD] ')
    tags = click.prompt('\_tags[tag1 tag2] ')
    tags_format = tags.encode('utf-8').split()

    os.chdir(pages_path)
    init_new_code = '''title: %s
date: %s
tags: %s

'''% (title.encode('utf-8'), date.encode('utf-8'), tags_format)
    init_code('%s.md' % post, init_new_code)

    logger.info('''
        \033[33m{info}\033[0m
        ==> add new blog in pages!
        '''
    )


@click.command()
def upload():
    """
    deploy blog on github
    """
    run_in_root(os.getcwd())
    os.popen('python blog.py build')
    logger.info('''
        \033[33m{info}\033[0m
        ==> deploy your blog on github!
        '''
    )


@click.command()
def runserver():
    """
    run the blog on localhost
    """
    run_in_root(os.getcwd())
    os.popen("python blog.py")


# cli command set
cli.add_command(init)
cli.add_command(upgrade)
cli.add_command(new)
cli.add_command(upload)
cli.add_command(runserver)

