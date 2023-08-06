# coding: utf-8

init_hello_code = '''title: hello from cat
date: 2016-01-23
tags: ['hello', 'cat']
img: http://7xj431.com1.z0.glb.clouddn.com/catg

cat
===
python家的静态博客生成器<br/>
![cat](http://7xj431.com1.z0.glb.clouddn.com/haha.gif)

### 安装(pip install catg)

    $ pip install catg

### 生成blog

    $ ca init

(注: 以下所有命令需在<code>blog/</code>下运行)
### 添加新博文

    $ ca new post
    \_title:
    \_date[YYYY-MM-DD]:
    \_tags[tag1 tag2]:

### 预览博客

    $ ca runserver
    访问 http://127.0.0.1:5000 即可预览博客

### 部署博客
要求使用github pages进行部署
#### 1. 注册一个github账号
#### 2. 创建一个仓库, 仓库名: <code>github用户名.github.io</code>
#### 3. 配置<code>config.py</code>的<code>GIT_URL</code>为创建仓库的git地址(https协议)
#### 4. 本地运行<code>$ ca upload</code>部署博客
#### 5. 访问 http://github用户名.github.io 即可看到你的博客(可能需要等一会)

### 默认主题 cat
![cat](http://7xj431.com1.z0.glb.clouddn.com/cattheme)

### 配置博客
采用**python类**的语法进行配置(都是程序员嘛,就像nginx配置一样😄 ), 示例:

    """
    默认配置
    --> DEBUG: debug模式
    --> FLATPAGES_AUTO_RELOAD
    --> FLATPAGES_EXTENSION ==> flask-flatpages 配置
    """
    class Config:
        DEBUG = True
        FLATPAGES_AUTO_RELOAD = DEBUG
        FLATPAGES_EXTENSION = '.md'

    """
    个人配置
    --> BLOG_TITLE: 博客标题
    --> BLOG_URL: 博客URL地址
    --> BLOG_DESCRIPTION: 博客描述
    --> BLOG_KEYWORDS: 这个博客的关键字
    --> BLOG_THEME: 博客主题
    --> GIT_URL: 部署至github仓库的url
    """
    class MyConfig(Config):
        BLOG_TITLE = "cat^0^python家的静态博客生成器"
        BLOG_URL = "http://127.0.0.1:5000"
        BLOG_DESCRIPTION = "python static blog generator"
        BLOG_KEYWORDS = "python static blog cat"
        GIT_URL = "https://github.com/neo1218/neo1218.github.io.git"

    """有效配置名称"""
    config = {
        'default': MyConfig
    }

## 编写主题
使用 html(jinja2模版), css, js 编写主题, 可以编写的页面如下表: <br/>
![table](http://7xj431.com1.z0.glb.clouddn.com/table)

## 更换主题

0. 查看[cat主题收录列表](https://github.com/neo1218/cat/tree/master/cat/theme),找到自己喜爱的主题
1. clone github上相应主题到theme目录下
2. 运行<code>ca upgrade theme_name</code>更新主题(theme_name为theme目录下相应主题的目录名)
'''
