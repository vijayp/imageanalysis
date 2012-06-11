#!/usr/bin/env python
# Copyright Vijay Pandurangan (vijayp@vijayp.ca) 2012
# Apache 2.0 Licence

from PIL import Image, ImageDraw, ImageFont
from GChartWrapper import Pie
import cPickle
from collections import defaultdict
import colorsys
import argparse
import sys
import os
import json

GREY = 'grey'
BLACK = 'black'
WHITE = 'white'
HUE_DEGREES_NAME = {
    GREY: 'grey',
    BLACK: 'black',
    WHITE: 'white',
    0 : 'red',
    30 : 'orange',
    60 : 'yellow',
    90 : 'green-yellow',
    120: 'green',
    150: 'cyan-green',
    180: 'cyan',
    240: 'blue',
    300: 'magenta',
    330: 'red-magenta',
    360: 'red'
}

def get_html_colour_from_hue(h):
    if h == GREY:
        return '777777'
    if h == BLACK:
        return '000000'
    if h == WHITE:
        return 'ffffff'
        
    rgb = colorsys.hls_to_rgb(h/360.0,0.5,0.5)
    return '%02x%02x%02x' % (rgb[0]*255,rgb[1]*255,rgb[2]*255)
    
get_pil_clist = lambda fn:Image.open(fn).getcolors(1<<20)
remove_rare_colors = lambda l: [x for x in l if x[0] > 2]
MAX_VALUE = float(1<<8)
BRIGHTEST = 0.99
GREY_BORDER = 0.03
BLACK_BORDER = 0.01
SATURATION_GREY = 0.03
args = None
def SetCLA():
    parser = argparse.ArgumentParser(description='Generate color spectra.')
    parser.add_argument('files', metavar='List of Directories', type=str, nargs='*',
                        help='list of files. used iff --cpkin is not set', 
                        default=[])
    parser.add_argument('--outdir', type=str, 
                        help='output directory for the data',
                        required=True)
    parser.add_argument('--cpkout', type=str, help='data output file')
    parser.add_argument('--label', type=str, help='label for image')
    parser.add_argument('--cpkin', type=str, 
                        help="input data file. If this is set, we don't open files")
    global args
    args = parser.parse_args()
    

class ImageDataAggregator(object):
    def  __init__(self, max_possible_colours):
        self._numcolours = max_possible_colours
        self._accumulator = [[0,0,0] for _ in xrange((max_possible_colours+3))]
        self._white_index = max_possible_colours
        self._grey_index = max_possible_colours + 1
        self._black_index = max_possible_colours + 2
        self._colour_counts = defaultdict(int)

    def _ProcessPixel(self, count_rgb):
        count, rgb = count_rgb
        rgb = (rgb[0]/MAX_VALUE,
               rgb[1]/MAX_VALUE,
               rgb[2]/MAX_VALUE)
        try:
            h,l,s = colorsys.rgb_to_hls(*rgb)
        except ZeroDivisionError, e:
            print e
            return 
        
        key = None
        if l > BRIGHTEST:
            key = self._white_index
            self._colour_counts['white'] += count
        elif GREY_BORDER > l > BLACK_BORDER: 
            key = self._grey_index
            self._colour_counts['grey'] += count
        elif BLACK_BORDER > l:
            key = self._black_index
            self._colour_counts['black'] += count
        elif s < SATURATION_GREY:
            key = self._grey_index
            self._colour_counts['grey'] += count
        else:
            key = int(self._numcolours*h)
            hue_degrees = h * 360 
            dists = []
            for k,v in HUE_DEGREES_NAME.items():
                if isinstance(k, str): 
                    continue
                
                dists.append((abs(hue_degrees - k),k))
            md = min(dists)[1]

            if md == 360: md = 0
            self._colour_counts[md] += 1
            
        self._accumulator[key][0] += count
        self._accumulator[key][1] += l
        self._accumulator[key][2] += s
#        print key, count, l, s, self._accumulator[key]

    def AddImage(self, filename):
        map(self._ProcessPixel, get_pil_clist(filename))
            
    
    def RGBWeightItems(self,ignore_grey=False,
                       ignore_colour=False,
                       ignore_lightness=False,
                       ignore_saturation=False):
        if ignore_grey:
            binrange = xrange(0, self._numcolours)
        elif ignore_colour:
            binrange = xrange(self._numcolours, self._numcolours+3)
        else:
            binrange = xrange((self._numcolours+3))
        total_count = float(sum([self._accumulator[x][0] for x in binrange]))
        rv = []
        for bin in binrange:
            (count, l_total, s_total) = self._accumulator[bin]
            if not count:
                continue
            if bin == self._white_index:
                h = 0
                l_avg = 0
                s_avg = 0
            elif bin == self._black_index:
                h = 1
                l_avg = 1
                s_avg = 0
            elif bin == self._grey_index:
                h = 1
                l_avg = GREY_BORDER
                s_avg = 0
            else:
                h = (bin + 0.5) / self._numcolours
                l_avg = l_total/count
                s_avg = s_total/count

            if ignore_saturation:
                s_avg = 0.5
            if ignore_lightness:
                l_avg = 0.5
            weight = count / total_count
            rgb = colorsys.hls_to_rgb(h, l_avg, s_avg)

            yield rgb, weight
#            rv.append((rgb, weight))
#        rv.sort(key=lambda x:x[1])
#        print rv[-10:]
#        assert 0

    #image = Image.new('RGB', (width, height))
    #canvas = Image.Draw(image)
    #del canvas
    #image.save(outfn, 'PNG')
    def SaveToFile(self, ofile):
        cPickle.dump(self, open(ofile, 'wb'))
    
    @staticmethod
    def CreateFromFile(ifile):
        return cPickle.load(open(ifile, 'r'))

    def DrawOnCanvas(self, height, width, hbase, canvas,
                     ignore_grey, ignore_colour, label=None,
                     ignore_saturation=False,
                     ignore_lightness=False):
        right_edge = 0
        if label is not None:
            f = ImageFont.load_default()
            canvas.text((0,0), label, font=f, fill=(255,255,255))
            # max label size
            right_edge += 50
        canvas.rectangle((0,hbase,right_edge+hbase+height+1, width+1),
                         outline=(1,0,0))
        right_edge += 1
        hbase += 1
        height -= 2
        width -=2

        assert width >= self._numcolours
        leftover = 0
        for rgb, weight in self.RGBWeightItems(ignore_grey, 
                                               ignore_colour,
                                               ignore_lightness,
                                               ignore_saturation):
            boxwidth = weight * width + leftover
            leftover = boxwidth - int(boxwidth)
            boxwidth = int(boxwidth)
            if not boxwidth: 
                continue
            rgb = tuple(map(lambda x:int(MAX_VALUE*x),rgb))
#            print map(hex, rgb), weight
            canvas.rectangle(map(int,(right_edge,hbase,
                             right_edge+boxwidth, hbase + height,)),
                             fill=rgb, outline=rgb)
            right_edge += boxwidth

    def DrawToFile(self, height, width, outfn, ignore_grey, ignore_colour,
                   label, 
                   ignore_lightness=False,
                   ignore_saturation=False):
        image = Image.new('RGB', (width+2, height+2))
        canvas = ImageDraw.Draw(image)
        self.DrawOnCanvas(height+2, width+2, 0, canvas,
                          ignore_grey, ignore_colour,
                          label=label,
                          ignore_lightness=ignore_lightness,
                          ignore_saturation=ignore_saturation
                          )
        del canvas
        print 'writing to %s' % outfn
        image.save(outfn, 'PNG')
        cnames = []
        ccolours = []
        ccounts = []
        tt = sum(self._colour_counts.values())
        for (k,v) in sorted(self._colour_counts.items()):
            pct = 100.0*v/tt
            cnames.append(HUE_DEGREES_NAME[k] + '(%2.1f%%)' % pct)
            ccolours.append(get_html_colour_from_hue(k))
            ccounts.append(pct)
        # PRINT PIE CHART
        try:
            pc = Pie(ccounts).title('Colour distribution for %s' % label).color(*ccolours).label(*cnames).size(650,400)
            return pc.url
        except:
            return '#'
        
        

SIZE = 256
def image_as_sparse_vector(fn):
    rv = blist.blist([0])
    rv*= SIZE**3
    for c, (r,g,b) in get_pil_clist(fn):
        rv[(r*SIZE**2+g*SIZE+b)] = c
    return rv

def aggregate(paths):

    ida = ImageDataAggregator(1280)
    for path in paths:
      for (path, dirs, files) in os.walk(path):
        for f in files:
            if f.startswith('t_') and f.endswith('jpg'):
                fn = os.path.join(path, f)
                print fn
                ida.AddImage(fn)
    return ida

if __name__ == '__main__':
  SetCLA()
  assert args.files or args.cpkin, 'need files or input file'
  assert args.cpkin or args.cpkout, 'need output cpk file if no input file'
  assert args.outdir, ' need output dir'


  if args.cpkin:
      ida = ImageDataAggregator.CreateFromFile(args.cpkin)
  else:
      ida = aggregate (args.files)
      ida.SaveToFile(args.cpkout)
  for ig in {True, False}:
      for ic in {True, False}:
          for il in {True, False}:
              for igs in {True, False}:
                  if (il or igs) and (not ig or ic):
                      continue
                  make_name = lambda x: 'no' if x else ''
                  fnbase = os.path.join(
                      args.outdir,
                      '%sgrey.%scolour.%slight.%ssat.%s' % (
                          make_name(ig),
                          make_name(ic),
                          make_name(il),
                          make_name(igs),
                          args.label))
                      
                  cc = ida.DrawToFile(10, 1280, fnbase + '.png',
                                      ig, 
                                      ic, 
                                      args.label,
                                      il, 
                                      igs
                                      )
                  json.dump(cc, 
                            open(fnbase + '.json','wb'))


