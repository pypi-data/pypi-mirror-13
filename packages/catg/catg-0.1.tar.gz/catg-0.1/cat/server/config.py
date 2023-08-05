# coding: utf-8

init_config_code = '''# coding: utf-8

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
 --> GIT_URL: github page的url
"""
class MyConfig(Config):
    BLOG_TITLE = "cat^0^python家的静态博客生成器"
    BLOG_URL = "http://127.0.0.1:5000"
    BLOG_DESCRIPTION = "python static blog generator"
    BLOG_KEYWORDS = "python static blog cat"
    GIT_URL = ""


"""有效配置名称"""
config = {
    'default': MyConfig
}

'''
