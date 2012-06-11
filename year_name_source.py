#!/usr/bin/env python
import os
from collections import defaultdict
import cPickle
def get_movie_map(movie_path):
      rv = {}
      for (path, dirs, files) in os.walk(movie_path):
        for f in files:
            if f.endswith('.html') and f != 'index.html':
                mname = f[:-5].replace('-', ' ')
                mid = os.path.split(path)[-1]
                print mid, mname
                rv[int(mid)] = mname
      return rv

def get_year_map(movie_path):
    mid_mname_map = get_movie_map(movie_path)
    year_mname_map = defaultdict(set)
    for (path, dirs, files) in os.walk(movie_path):
        for f in files:
            if f.startswith('t_') and f.endswith('.jpg'):
                rem,mid = os.path.split(path)
                year = os.path.split(rem)[-1]
                val = mid_mname_map.get(int(mid), 'UNKNOWN')
                print year, val
                year_mname_map[year].add(unicode(val,errors='ignore'))
    for k,v in year_mname_map.iteritems():
        year_mname_map[k] = list(v)
    return year_mname_map
                
            


if __name__ == '__main__':
  import sys
  import os
  import json
  ym = get_year_map(sys.argv[1])
  json.dump(ym, open('year_data.json', 'wb'))
  
