import sys
import time, calendar
import BaseHTTPServer
import sqlite3

from getopt import getopt
reload(sys)
sys.setdefaultencoding('utf-8')
#sqlite> .schema
#CREATE TABLE posts (
#            thread INTEGER REFERENCES threads(thread),
#            id INTEGER,
#            author TEXT,
#            email TEXT,
#            trip TEXT,
#            time INTEGER,
#            body TEXT,
#            PRIMARY KEY (thread, id)
#        );
#CREATE TABLE threads (
#            thread INTEGER PRIMARY KEY,
#            title TEXT,
#            last_post INTEGER
#        );


PORT_NUMBER = 8080
FAGGOT_DATES = False

try:
   optlist, args = getopt(sys.argv[1:], '', ['faggot-dates', 'port='])
except:
   print "Bad args!"
   sys.exit(-1)

for (opt, arg) in optlist:
   if opt == '--faggot-dates':
      FAGGOT_DATES = True
   if opt == '--port':
      PORT_NUMBER = int(arg)

if FAGGOT_DATES:
   date_format = "%d %m %Y %H %M %S"
else:
   date_format = "%m %d %Y %H %M %S"

def generate_fp(board):
   fp = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>4chan BBS - Programming</title>
<link rel="stylesheet" href="http://static.4chan.org/css/dis/world4ch/global.css" />
<link rel="stylesheet" href="http://static.4chan.org/css/dis/world4ch/0ch.css" title="Pseud0ch" media="screen"/>
</head>
<body class="board">
  <div class="hborder">
    <div class="head">
   <div class="headtext">
      <h1>Programming</h1>
   </div>
    </div>
  </div>
 <div class="hborder">
  <div class="head threadldiv">
   <a name="menu" rev="contents"></a>
<ul class="threadlistflat" id="threadlist">
"""
   #top navigation
   x = 0
   for thread in board:
      if x <= 39:
         fp += """<li class="threadlink">"""
         fp += """<a href='read/prog/#%d/1-'>""" % (thread[0])
         fp += """%d: </a><a href='prog/#%d'>""" % (x+1, x+1)
         fp += """%s (%d)</a> </li>""" % (thread[1].title, thread[1].count)
         x += 1
      else: pass

   fp += """</ul><br/></div> </div>
"""

   x = 0
   for thread in board:
      if x <= 39:
        fp += """<div class="border"><a name="%d">""" % (x)
        fp += """</a><div class="thread"><div class="postheader">""" #<span class="navlinks"><a href="prog/#menu">&#9632;</a>&nbsp;<a href="prog/#%d" """ % (x - 1 if x > 1 else 40)
        #fp += """rel="prev">&#9650;</a>&nbsp;<a href="prog/#%d" """ % (x + 1 if x < 40 else 1)
        #fp += """rel="next">&#9660;</a></span>"""
        fp += """<h2><span class="replies">[%d:%d]</span> """ % (x, thread[1].count)
        fp += """<a name='%d' href='read/prog/%d'>""" % (thread[0], thread[0])
        fp += """%s</a></h2></div>""" % (thread[1].title)
        #w4ch seems to think 1 is even and 2 is odd
        fp += """<div class="post %s">""" % ( "even" if thread[1].posts[0].count % 2 == 1 else "odd") 
        fp += """<h3><span class="postnum">%d """ % (thread[1].posts[0].count)
        fp += """</span><span class="postinfo"><span class="namelabel"> Name: </span><span class="postername">%s""" % (thread[1].posts[0].author)
        fp += """</span><span class="postertrip"></span> : <span class="posterdate">%s""" % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(thread[1].posts[0].time)))
        fp += """</span> <span class="id"> </span></span></h3>"""
        fp += """<blockquote><p>"""
        fp += """%s""" % (thread[1].posts[0].body)
        fp += """</p</blockquote></div>"""
        if len(thread[1].posts) <= 5:
           for y in range(1,thread[1].count):
              fp += """<div class="post %s">""" % ( "even" if thread[1].posts[y].count % 2 == 1 else "odd") 
              fp += """<h3><span class="postnum">%d """ % (thread[1].posts[y].count)
              fp += """</span><span class="postinfo"><span class="namelabel"> Name: </span><span class="postername">%s""" % (thread[1].posts[y].author)
              fp += """</span><span class="postertrip"></span> : <span class="posterdate">%s""" % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(thread[1].posts[y].time)))
              fp += """</span> <span class="id"> </span></span></h3>"""
              fp += """<blockquote><p>"""
              fp += """%s""" % (thread[1].posts[y].body)
              fp += """</blockquote></p></div>"""
        else:
           fp += """<p class="hidden">The 5 newest replies are shown below.<br/>"""
           fp += """<a href="read/prog/%d/1-40">Read this thread from the beginning</a></p>""" % (thread[0])
           for y in range(len(thread[1].posts)-4,len(thread[1].posts)):
              fp += """<div class="post %s">""" % ( "even" if thread[1].posts[y].count % 2 == 1 else "odd") 
              fp += """<h3><span class="postnum">%d """ % (thread[1].posts[y].count)
              fp += """</span><span class="postinfo"><span class="namelabel"> Name: </span><span class="postername">%s""" % (thread[1].posts[y].author)
              fp += """</span><span class="postertrip"></span> : <span class="posterdate">%s""" % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(thread[1].posts[y].time)))
              fp += """</span> <span class="id"> </span></span></h3>"""
              fp += """<blockquote><p>"""
              fp += """%s""" % (thread[1].posts[y].body)
              fp += """</blockquote></p></div>"""
     
            
       
        fp += """</div></div>"""
        x += 1
      else: pass
   return fp


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
   def do_HEAD(s):
      s.send_response(200)
      s.send_header("Content-type", "text/html")
      s.end_headers()
   def do_GET(s):
      """Respond to a GET request."""

      con = sqlite3.connect("prog.db")

      s.send_response(200)
      s.send_header("Content-type", "text/html")
      s.end_headers()
      s.wfile.write("<html><head><title>Title goes here.</title></head>")
      arg_list = s.path.split("/")[1:]
      if arg_list == [''] or len(arg_list) < 6:
         s.wfile.write("lol need args")
         return

      time_string = ""
      for x in xrange(6):
         try:
            arg_list[x] = int(arg_list[x])
            time_string += "%d " % arg_list[x]
         except ValueError:
            s.wfile.write("You really should give me int dates!")
            return

      time_string = time_string[:-1]
      try:
         arg_time = time.strptime(time_string, date_format)
      except:
         s.wfile.write("Fix your time! It needs to be %s" % date_format)
         return

      class Post:
         def __init__(self, thread, count, author, email, trip, time, body):
            self.thread = thread
            self.count = count
            self.author = author
            self.email = email
            self.trip = trip
            self.time = time
            self.body = body

      class Thread:
         def __init__(self):
            self.posts = []
            self.count = 0
            self.title = ""
         def addpost(self, post):
            self.posts.append(post)
            self.count += 1

      class Board:
         def __init__(self):
            self.threads = []
            self.__threads = set()
         def addthread(self, threadid, thread):
            self.threads.append([threadid, thread])
            self.__threads.add(threadid)
         def __contains__(self, obj):
            return True if obj in self.__threads else False
         def __getitem__(self, obj): #this should suck
            for thread in self.threads:
               if thread[0] == obj:
                  return thread
         def __iter__(self):
            return self.threads.__iter__()
         def bump(self): #this bumps the last thread!
            foo = self.threads.pop()
            self.threads.insert(0, foo)
            

      board = Board() 

      posts = con.cursor()
      posts.execute("select * from posts where posts.time != 1234 and posts.time < %d order by time asc;" % calendar.timegm(arg_time))
      for post in posts:
         new_post = Post(post[0], post[1], post[2], post[3], post[4], post[5], post[6])
         if post[0] not in board:
            new_thread = Thread()
            new_thread.addpost(new_post)
            board.addthread(post[0], new_thread)
            board.bump()
         else:
            board[post[0]][1].addpost(new_post)
            board.bump()

      threads = con.cursor()
      threads.execute("select * from threads;")
      for thread in threads:
         if thread[0] in board:
            board[thread[0]][1].title = thread[1]

      s.wfile.write(generate_fp(board))
         
      s.wfile.write("</body></html>")
   def log_request(foo,bar):
      pass # no apache style logs


if __name__ == '__main__':
      server_class = BaseHTTPServer.HTTPServer
      httpd = server_class(('', PORT_NUMBER), MyHandler)
      try:
         httpd.serve_forever()
      except KeyboardInterrupt:
         pass
      httpd.server_close()
