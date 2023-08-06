# coding: utf-8

init_blog_code = '''# coding: utf-8
from flask import Flask, render_template, url_for
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from config import config
import shutil
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config.from_object(config['default'])
pages = FlatPages(app)
freezer = Freezer(app)

@app.route('/index/')
def index():
    posts = (p for p in pages if 'date' in p.meta)
    latests = sorted(posts, reverse=True, key=lambda x:x.meta['date'])
    tags = []
    archive = []
    for p in pages:
        tags = [tag for tag in p.meta.get('tags') if tag not in tags]
        year = str(p.meta.get('date'))[:-3]
        if year not in archive:
            archive.append(year)
    return render_template(
        'index.html', latests=latests,
        tags=tags,
        archive=archive,
        blog_title=app.config['BLOG_TITLE'],
        blog_url=app.config['BLOG_URL'],
        blog_description=app.config['BLOG_DESCRIPTION'],
        blog_keywords=app.config['BLOG_KEYWORDS']
    )

@app.route('/<path:path>/')
def page(path):
    tags = []
    archive = []
    for p in pages:
        tags = [tag for tag in p.meta.get('tags') if tag not in tags]
        year = str(p.meta.get('date'))[:-3]
        if year not in archive:
            archive.append(year)
    post = pages.get_or_404(path)
    return render_template('post.html',
        post=post,
        tags=tags,
        archive=archive
    )

@app.route('/tags/<string:tag>/')
def tags(tag):
    """获取相应tag下的所有博文"""
    posts = [p for p in pages if tag in p.meta.get('tags', [])]
    posts_num = len(posts)
    return render_template('tags.html',
        tag = tag,
        posts = posts,
        posts_num = posts_num
    )

@app.route('/archive/<string:year>/')
def archive(year):
    """博文归档"""
    posts = [p for p in pages if year in str(p.meta.get('date'))[:-3]]
    posts_num = len(posts)
    return render_template('archive.html',
        posts = posts,
        year = year,
        posts_num = posts_num
    )

def upload():
    os.chdir(build_path)
    os.popen('git add .')
    os.popen('git commit -m "cat blog update"')
    os.popen('git push -u %s master' % app.config['GIT_URL'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    elif len(sys.argv) > 1 and sys.argv[1] == "upload":
        upload()
    else:
        app.run(debug=True)
'''
