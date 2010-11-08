import sys
import time, calendar
import BaseHTTPServer
import sqlite3

from getopt import getopt
reload(sys)
sys.setdefaultencoding('utf-8')

import operator

PORT_NUMBER = 8080
FAGGOT_DATES = False
db_name = None

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

if len(args) > 0:
   db_name = args[0]
elif not db_name:
   db_name = "prog.db"


if FAGGOT_DATES:
   date_format = "%d %m %Y %H %M %S"
else:
   date_format = "%m %d %Y %H %M %S"

och_css = "a:link,a:visited{color:blue;}a:hover,a:active{color:red;}body.board,body.list{margin:0;}body.board{background-image:url('/ba.gif');margin-top:1.5em;}body.read{background-color:#efefef;}.head,body.board .thread{border:1px inset gray;padding:6px;}table.postform td{text-align:left;}table.postform td input{width:auto;}table.newthreadform .submit{width:100%;}table.postform td textarea{width:auto;}table.postform td.label{text-align:right;}table.postform .mail{width:auto;float:right;}input.submit{float:right;}.legal{text-align:center;font-size:small;}.manage{text-align:center;font-size:x-small;}.postnum{font-weight:bold;margin-right:.1em;}.postername,.postertrip{color:green;}.postername{font-weight:bold;}blockquote{text-align:left;font-family:serif;margin-top:.5em;}blockquote p{margin-top:0;}.border,.hborder{border:1px outset gray;margin-left:2.5%;margin-right:2.5%;width:95%;padding:6px;margin-bottom:1em;background-color:#efefef;}.hborder{background-color:#cfc;}h2{margin-top:0;clear:both;}.threadlinks{display:block;text-align:right;}.threadlinks a{font-weight:bold;}.threads{font-size:small;text-align:left;}table.threads th{text-align:center;}.styles{border:2px outset black;margin:2px;background:white;float:left;margin-top:0;margin-left:0;}.threads th a,.threads td a,.postfieldleft a,.postnum a{color:black;}.postfieldleft a,.postnum a,h2 a{text-decoration:none;}.postfieldleft{vertical-align:top;}.replies{font-size:70%;font-weight:bolder;}h2 a:link,h2 a:visited,h2 a:active,h2 a:hover{color:red;}h2 a:hover,h2 a:active{text-decoration:underline;}h2,.navlinks{clear:none;margin-bottom:.1em;}.pages{font-size:smaller;}.bottomnav{text-align:center;}.newthread h2{color:black;}.postinfo{margin-left:.3em;}.navlinks a{font-family:IPAMonaPGothic,Mona,'MS PGothic',YOzFontAA97;}h3{font-weight:normal;font-size:100%;margin-top:0;margin-bottom:0;}.tolder{font-size:90%;}body.read h2{color:red;font-size:larger;}.threadlistflat{display:inline;padding:0;margin:0;}.threadlink{display:inline;text-align:justify;}.pages{text-align:center;font-size:small;}.navlinks{float:right;}.navlinks a{text-decoration:none;}.threadlink{padding-right:.55em;}.boldthreadlink{padding-right:.55em;font-weight:bold;}.stylelist{display:inline-block;float:right;}#ad div.ad-title a,.bottomAdFoot a:hover,.adText,.bottomAdTitle,.postblock{color:black;}#bottomAdOuter{border:1px solid #cfc;}.bottomAdTitle{font-size:11px;background:#efefef;font-weight:bold;}.postblock{background:#efefef;}"

global_css = ".quote{border-left:solid 2px #666;padding:0 0 0 10px;margin:3px 0;display:block;}.quote .quote{border-left:solid 2px #888;}.quote .quote .quote{border-left:solid 2px #aaa;}.quote:hover{background:#f0f0e0;}.spoiler{background:#000;color:#000;}.spoiler:hover{color:#FFF;}.aa{text-align:left;font-family:IPAMonaPGothic,Mona,'MS PGothic',YOzFontAA97!important;}.o{text-decoration:overline;}tt{font-size:smaller;}h1{text-align:center;margin:0 auto;}.navlinks{float:right;}.navlinks a{text-decoration:none;}.legal,.manage{margin-bottom:.3em;}.postform td textarea{resize:vertical;}#ad div.ad-title a,.bottomAdFoot a,.bottomAdFoot a:hover{font-family:sans-serif;}#ad div.ad-text a{font-family:sans-serif;}.adHeadline{font-family:sans-serif;font-size:11px;font-weight:normal;}.adText{font-family:sans-serif;font-size:11px;font-weight:normal;text-decoration:none;}#bottomAdOuter{width:600px;font-size:11px;}.bottomAdTitle{font-family:sans-serif;}#bottomAd{height:52px;font-size:11px;}.options{text-align:center;}.navmenus{display:inline;display:inline-block;}.navmenus form{display:inline;}.headtext{margin:.5em auto;}.subhead{text-align:center;font-size:smaller;}.capcode{font-weight:bold;color:#f00;}.emailfield{display:none;width:0;}.str{color:#080;}.kwd{color:#008;}.com{color:#800;}.typ{color:#606;}.lit{color:#066;}.pun{color:#660;}.tag{color:#008;}.atn{color:#606;}.atv{color:#080;}.dec{color:#606;}pre.prettyprint{padding:2px;border:1pxsolid #888;}@media print{.str{color:#060;}.kwd{color:#006;font-weight:bold;}.com{color:#600;font-style:italic;}.typ{color:#404;font-weight:bold;}.lit{color:#044;}.pun{color:#440;}.tag{color:#006;font-weight:bold;}.atn{color:#404;}.atv{color:#060;}}"

import base64
ba_gif = base64.b64decode("R0lGODlhPAA8AJEAANzAptCznMWtmbOekiH5BAQUAP8ALAAAAAA8ADwAAAL/nI+py+0YnpzUCRGyDnjzC4bipXWeBgBnKaRuNgpDmKll4Oa6jvN1ihNFLCJEa4WDeWIjgOmzAX1InOGhukxJe5kBVChLopwmgPcyw8hmwC11YBsOhVjOK5neeGGdq9ZUBJUWRhU11uLEpsfSZdBDwjQV0RFWc6Li1dZyoVVlcoCoBsk0ShN1RPby9KVm9SgVGanEh2HzstfDVnhwBznDMUi6Uhu34VLowQtUEmww8ru62pMCZ+tsA+ioCUJWSdo6RaxyV6PtXOVHJgkCFz6yVOWUM0VtkEir7XQjdYYmSzvtxzhsJKAByxSnVIRJ336FG/hD3CJP9pbBYgcwRBpc/8bI2fnYQR+MitigYaSlUdoYS4XaRNmIUBK+byqn7ZhHjGWimGocQqlzCUU5aM7QgHpwZFAwGUybzqgAVcGfNVEdzBuzbEUORDyW3bxpLMw8dYUIcc0qRoOjjh62TkszsN6sUn/qFJMzrFJatSSAYOJ44giXjoiA0nGXsnCudjfi3NWK5CLDZzX6TrrbCahWGoLfIPb1g48ueEhuoET2E6XS0GYuG3pUOrLk0884qZBhpsVGSj4js4C0RBihNl5MBos9CyUjd3xEc9bNeJClzcOWewPjrxbL6DWnnxL1ZMvvIi0bkTkOA+3E5r+/u7myBI4/rYBFav4YWKZRwSy6tf/CtpByyVUXGBUh2FKCDbjcZl9bsQECj4ELCoVbcv6FJgZ/SliECxP2CERIWjsIdFc0irlyHzpwLHDQUjRld04RCVC1AI0yOqPAi+LpiBpJX/2oQ0hADvlVcLPF0EiAnTTk0EXasHPbczEopUw3/Xii1h7NfJhHhsC5xw58UUrzSVl9YMARIAYCFA4CW+kVTXIpSacmKS5SNc1zknQZJlPSJQTeB/34h6NHA7525hrL7cPORYEg9JiRkdhzWHs0sYHQgSM9qEc/RmX0DhOtbZMlWYFg1Od4l9KQaYqiLVrKOaoiOVlxobAXHG1uMHXKZ3aKFWmuBpYSqodTNlqNJgUpircnsWBmd6qfXMCC3EiiZASqKVMWNxhyJuKaWh1SOsqterI5apkUBQAAOw==")

def generate_thread(board):
   fp = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>4chan BBS - %s</title>
<link rel="stylesheet" href="/global.css" />
<link rel="stylesheet" href="/0ch.css" title="Pseud0ch" media="screen"/>
</head>
<body class="read">
""" % (board.threads[0][1].title)
   fp += """<h2>%s</h2><div class="thread">""" % (board.threads[0][1].title)
   for post in board:
      for x in range(board.threads[0][1].count):
         #w4ch seems to think 1 is even and 2 is odd
         fp += """<div class="post %s">""" % ( "even" if board.threads[0][1].count % 2 == 1 else "odd") 
         fp += """<h3><span class="postnum">%d """ % (board.threads[0][1].posts[x].count)
         fp += """</span><span class="postinfo"><span class="namelabel"> Name: </span><span class="postername">%s""" % (board.threads[0][1].posts[x].author)
         fp += """</span><span class="postertrip"></span> : <span class="posterdate">%s""" % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(board.threads[0][1].posts[x].time)))
         fp += """</span> <span class="id"> </span></span></h3>"""
         fp += """<blockquote><p>"""
         fp += """%s""" % (board.threads[0][1].posts[x].body)
         fp += """</p</blockquote></div>"""
         fp += """</div></div>"""
   return fp


def generate_fp(board):
   fp = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>4chan BBS - Programming</title>
<link rel="stylesheet" href="/global.css" />
<link rel="stylesheet" href="/0ch.css" title="Pseud0ch" media="screen"/>
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
         fp += """<a href="./read/prog/%d/1-">""" % (thread[0])
         fp += """%d: </a><a href='#%d'>""" % (x+1, x+1)
         fp += """%s (%d)</a> </li>""" % (thread[1].title, thread[1].count)
         x += 1
      else: pass

   fp += """</ul><br/></div> </div>
"""

   x = 0
   for thread in board:
      if x <= 39:
        fp += """<div class="border"><a name="%d">""" % (x+1)
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
           fp += """<a href="read/prog/%d/">Read this thread from the beginning</a></p>""" % (thread[0])
           for y in range(len(thread[1].posts)-4,len(thread[1].posts)):
              fp += """<div class="post %s">""" % ( "even" if thread[1].posts[y].count % 2 == 1 else "odd") 
              fp += """<h3><span class="postnum">%d """ % (thread[1].posts[y].count)
              fp += """</span><span class="postinfo"><span class="namelabel"> Name: </span><span class="postername">%s""" % (thread[1].posts[y].author)
              fp += """</span><span class="postertrip"></span> : <span class="posterdate">%s""" % (time.strftime("%Y-%m-%d %H:%M", time.gmtime(thread[1].posts[y].time)))
              fp += """</span> <span class="id"> </span></span></h3>"""
              fp += """<blockquote><p>"""
              fp += """%s""" % (thread[1].posts[y].body)
              fp += """</blockquote></p></div>"""
        fp += """<a href="read/prog/%d/">Entire thread</a></p>""" % (thread[0]) 
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

      con = sqlite3.connect(db_name)

      arg_list = s.path.split("/")[1:]

      if s.path == "/ba.gif":
         s.send_response(200)
         s.send_header("Content-type", "image/gif")
         s.end_headers()
         s.wfile.write(ba_gif)
         return

      if arg_list[0] == "0ch.css":
         s.send_response(200)
         s.send_header("Content-type", "text/css")
         s.end_headers()
         s.wfile.write(och_css)
         return
      
      if arg_list[0] == "global.css":
         s.send_response(200)
         s.send_header("Content-type", "text/css")
         s.end_headers()
         s.wfile.write(global_css)
         return

      #this fixes a bug caused by forgetting a trailing slash
      if s.path[-1] != "/":
         s.send_response(301)
         s.send_header("Location", "http://localhost:%d%s/" % (PORT_NUMBER, s.path))
         return


      s.send_response(200)
      s.send_header("Content-type", "text/html")
      s.end_headers()

      if arg_list == [''] or len(arg_list) < 6:
         s.wfile.write("Need more arguments!  URLs are in the format http://localhost:%d/%s" % (PORT_NUMBER, date_format.replace(" ", "/")))
         return

      time_string = ""
      for x in xrange(6):
         try:
            arg_list[x] = int(arg_list[x])
            time_string += "%d " % arg_list[x]
         except ValueError:
            s.wfile.write("You really should give me int dates!")
            return

      thread_id = False
      try:
         thread_id = int(arg_list[8])
      except ValueError:
         s.wfile.write("Threads need to be ints!")
         return
      except IndexError:
         pass

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
            self.threads.insert(0, [threadid, thread])
            self.__threads.add(threadid)
         def __contains__(self, obj):
            return True if obj in self.__threads else False
         def __getitem__(self, obj): #this should suck
            for thread in self.threads: #reversed?
               if thread[0] == obj:
                  return thread[1]
            #return self.threads[self.threads.index([obj, self[obj]])]
            return False

         def __iter__(self):
            return self.threads.__iter__()
         def bump(self,thread):
            foo = self.threads.pop(self.threads.index([thread, self[thread]]))
            self.threads.insert(0, foo)
            
      board = Board() 

      latest = con.cursor()
      fp_posts = con.cursor()
      posts = []

      if not thread_id: #we want the entire board
         latest.execute("select distinct thread from posts where posts.time != 1234 and posts.time < %d order by time desc limit 40;" % calendar.timegm(arg_time)) # last 40
         for post in latest:
            fp_posts.execute("select * from posts where posts.thread = ? and posts.time != 1234 and posts.time < ? order by time;", (post[0], calendar.timegm(arg_time)))
            for fp_post in fp_posts:
               post_tbd = [fp_post[0], fp_post[1], fp_post[2], fp_post[3], fp_post[4], fp_post[5], fp_post[6]]
               if post_tbd not in posts:
                  posts.append(post_tbd)
         posts = sorted(posts, key=operator.itemgetter(5))
            
      else:
         #but getting a single thread is fast!
         latest.execute("select * from posts where posts.thread = ? and posts.time != 1234 and posts.time < ? order by time asc;", (thread_id, calendar.timegm(arg_time)))
         posts = latest

      for post in posts:
         new_post = Post(post[0], post[1], post[2], post[3], post[4], post[5], post[6])
         if not board[post[0]]:
            new_thread = Thread()
            new_thread.addpost(new_post)
            board.addthread(post[0], new_thread)
         else:
            board[post[0]].addpost(new_post)
            board.bump(post[0])

      threads = con.cursor()
      threads.execute("select * from threads;")
      for thread in threads:
         if board[thread[0]]:
            board[thread[0]].title = thread[1]

      # catch stuff
      if thread_id != 0:
         s.wfile.write(generate_thread(board))
         return

      # if nothing else, do fp
      s.wfile.write(generate_fp(board))
      s.wfile.write("</body></html>")
   def log_request(foo,bar):
      pass # no apache style logs


if __name__ == '__main__':
      server_class = BaseHTTPServer.HTTPServer
      httpd = server_class(('', PORT_NUMBER), MyHandler)
      print "rewind.py [--faggot-dates] [--port=n] [prog.db]"
      print "Browse to http://localhost:%d/" % PORT_NUMBER
      print "It may take 20 seconds or more to generate the front page."
      try:
         httpd.serve_forever()
      except KeyboardInterrupt:
         pass
      httpd.server_close()

