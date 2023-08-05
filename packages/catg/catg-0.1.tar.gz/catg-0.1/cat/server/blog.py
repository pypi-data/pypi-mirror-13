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
    post = pages.get_or_404(path)
    return render_template('post.html', post=post)

@app.route('/tags/<string:tag>/')
def tags(tag):
    """获取相应tag下的所有博文"""
    posts = [p for p in pages if tag in p.meta.get('tags', [])]
    return "<h1>this is just a test for tags</h1>"

@app.route('/archive/<string:year>/')
def archive(year):
    """博文归档"""
    posts = [p for p in pages if year in str(p.meta.get('date'))[:-3]]
    return "<h1>this is just a test for archive</h1>"

def upload():
    build_path = os.path.join(os.getcwd(), 'build')
    index_path = os.path.join(build_path, 'index/index.html')
    index_target_path = os.path.join(build_path, 'index.html')
    shutil.copy(index_path, index_target_path)
    os.chdir(build_path)
    os.popen('git init')
    os.popen('git pull %s master' % app.config['GIT_URL'])
    os.popen('git add .')
    os.popen('git commit -m "cat blog update"')
    os.popen('git push -u %s master' % app.config['GIT_URL'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
        upload()
    else:
        app.run(debug=True)
'''
