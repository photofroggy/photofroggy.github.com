#!/usr/bin/python
import os
import sys
import json
import os.path
from datetime import date

"""
Helper classes and functions for the blog.
This is part of my ongoing effort to overcomplicate
everything in the world ever.
"""

MONTH = [ 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december' ]


def say(msg):
    """
    Write msg to stdout.
    Don't forget to flush!
    """
    sys.stdout.write('>> ' + msg + '\n')
    sys.stdout.flush()


class Archive(object):
    """
    Represents the archive for the blog
    """
    
    def __init__(self, path='blog/entries.json', blog='blog', template='blog/template.html'):
        self.path = path
        self.blog = blog
        self.template = template
        self.items = []
        self.load()
    
    def load(self):
        """
        Load the archive from our entries file.
        Resulting data is stored in self.items.
        """
        f = open(self.path, 'r')
        d = f.read()
        f.close()
        self.items = json.loads(d)
    
    def save(self):
        """
        Save the archive to our entries file.
        """
        f = open(self.path, 'w')
        f.write(json.dumps(self.items))
        f.close()
    
    def new(self, title, filename=None):
        """
        Add a new item to the archive.
        Returns the assumed filepath for the blog post.
        """
        filename = (filename or title).lower().replace(' ', '_')
        
        # Timestamp stuff.
        stamp = date.today()
        m = MONTH[stamp.month - 1]
        dayn = stamp.day
        days = str( dayn )
        dlast = int( days[-1] )
        day = ''
        y = str(stamp.year)
        
        # Figure out whether the day is the n-st, n-nd, n-rd or n-th of the mnth.
        if dayn >= 10 and dayn <= 20:
            day = days + 'th'
        else:
            if dlast == 1:
                day = days + 'st'
            if dlast == 2:
                day = days + 'nd'
            if dlast == 3:
                day = days + 'rd'
            if dlast > 3:
                day = days + 'th'
        
        # file path stuff.
        fold = '{0}/{1}/{2}'.format( self.blog, y, m )
        fpath = (fold + '/' + filename + '.html').lower()
        
        # Add the post to the archive list
        self.items.insert( 0, { 'href': fpath[ len(self.blog) + 1 : ], 'title': title } )
        self.save()
        
        # Make sure the folder exists.
        if not os.path.exists( self.blog + '/' + y ):
            os.path.mkdir( self.blog + '/' + y, 0o755 )
        
        if not os.path.exists( fold ):
            os.path.mkdir( fold, 0o755 )
        
        self.new_template( fpath, title, '{0} {1}, {2}'.format( day, m.title(), y ) )
        
        return fpath
    
    def new_template(self, path, title, stamp):
        """
        Create a template for a blog post.
        """
        # Read template
        tf = open( self.template, 'r' )
        templ = tf.read()
        tf.close()
        
        # Save template.
        newpost = open( path, 'w' )
        newpost.write( templ.format( title, stamp ) )
        newpost.close()
    
    def publish(self, index=0):
        """
        Publish the entry at the given index as the home of the blog.
        """
        post = self.get(index)
        
        if post is None:
            return False
        
        try:
            pfile = open(self.blog + '/' + post['href'], 'r')
            content = pfile.read()
            pfile.close()
            
            pfile = open(self.blog + '/index.html', 'w')
            pfile.write(content.replace('../../', ''))
            pfile.close()
        except Exception:
            return False
        
        return True
    
    def get(self, index=0):
        """
        Get the archive entry at the given index.
        If no entry is found, None is returned.
        """
        if len(self.items) <= index:
            return None
        
        return self.items[index]
    
    def remove(self, index=0):
        """
        Remove the archive entry at the given index.
        Return True on success, False on failure.
        """
        entry = self.get(index)
        
        if entry is None:
            return False
        
        try:
            os.remove( self.blog + '/' + entry['href'] )
        except Exception as e:
            return False
        
        self.items.pop(index)
        self.save()
        self.load()
        
        return True
    
    def find(self, title):
        """
        Find an archive entry by the title of the entry.
        Returns the index. -1 is not found.
        """
        title = title.lower()
        
        for index, item in enumerate(self.items):
            if item['title'].lower() == title.lower():
                return index
        
        return -1
    
    def removeTitle(self, title):
        """
        Find and remove an archive entry with the given title.
        Returns a boolean.
        """
        index = self.find(title)
        
        if index == -1:
            return False
        
        return self.remove(index)

