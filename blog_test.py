import os
import re
import random
import hashlib
import hmac
from datetime import datetime, timedelta
from google.appengine.api import memcache
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def link(self, a):
        return "/blog/" + str(a)

    def link_edit(self, a):
        return "/blog/edit/" + str(a)


    def render_blogfront(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

    def render_permalink(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("postpermalink.html", p = self)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # def set_secure_cookie(self, name, val):
    #     cookie_val = make_secure_val(val)
    #     self.response.headers.add_header(
    #         'Set-Cookie',
    #         '%s=%s; Path=/' % (name, cookie_val))

    # def read_secure_cookie(self, name):
    #     cookie_val = self.request.cookies.get(name)
    #     return cookie_val and check_secure_val(cookie_val)

    # def login(self, user):
    #     self.set_secure_cookie('user_id', str(user.key().id()))

    # def logout(self):
    #     self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # def initialize(self, *a, **kw):
    #     webapp2.RequestHandler.initialize(self, *a, **kw)
    #     uid = self.read_secure_cookie('user_id')
    #     self.user = uid and User.by_id(int(uid)) 
class EditPost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
#        params = dict(subject = post.subject)

        self.render("test_wiki.html", post=post)

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("test_wiki.html", subject=subject, content=content, error=error)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class MainPage(BlogHandler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render('front.html', posts = posts)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/newpost', NewPost),
                                ('/blog/([0-9]+)', PostPage),
                                ('/blog/edit/([0-9]+)', EditPost),
                               ],
                              debug=True)