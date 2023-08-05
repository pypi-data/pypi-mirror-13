# coding: utf-8

init_hello_code = '''title: hello from cat
date: 2016-01-23
tags: ['hello', 'cat']

cat
===
python家的静态博客生成器<br/>
![cat](http://7xj431.com1.z0.glb.clouddn.com/haha.gif)

### 安装

    $ pip install cat

### 生成blog

    $ ca init blog

### 添加新博文

    $ ca new
    \_title:
    \_category:
    \_tag:


### 预览博客

    $ ca runserver
    访问 http://127.0.0.1:5000 即可预览博客

### 部署博客
要求使用github pages进行部署

    $ ca upload

### 默认主题 cat
![cat](http://7xj431.com1.z0.glb.clouddn.com/cattheme)

### 配置博客
采用**python类**的语法进行配置(都是程序员嘛,就像nginx配置一样😄 ), 示例:

    class Config:
        DEBUG = True
        FLATPAGES_AUTO_RELOAD = DEBUG
        FLATPAGES_EXTENSION = '.md'
        BLOG_TITLE = "cat^0^python家的静态博客生成器"
        BLOG_URL = "http://127.0.0.1:5000"
        BLOG_DESCRIPTION = "python static blog generator"
        BLOG_KEYWORDS = "python static blog cat"

    config = {
        'default': Config
    }


Config类是公有配置, 可以在继承Config类的基础上创建自己的配置, 比如:

    class MyConfig(Config):
        """
        配置
        """

    config = {
        'default': MyConfig
    }

## 编写主题
使用 html(jinja2), css, js 编写主题, 可以编写的页面如下表


## 更换主题

1. clone github上相应主题到theme目录下
2. 只需更改配置文件(config.py)中的THEME配置项为相应主题的名字

'''
