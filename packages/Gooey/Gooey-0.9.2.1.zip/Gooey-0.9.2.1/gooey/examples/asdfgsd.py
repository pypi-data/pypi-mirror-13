'''
          gooeyCheckboxesProblem.py
@summary  Some checkboxes do not react to user input at all.
@author   https://github.com/drandreaskrueger
@bitcoin  1GdYteTSMUgiKdm1M4Yim7YdLoAoeME8kj
@since    Created on 28 Jan 2016
@abstract This shows the combinations that are ill:
Run 1: Just press Start.
Run 2: Switch ALL checkboxes to opposite values.
Output: 
Run 1: fine:  False False      broken:   True False
Run 2: fine:   True  True      broken:   True False
  
Gooey 0.9.2 ; wx 3.0.0.0 ; Python 2.7.11 |Anaconda 2.4.1 (64-bit)| (default, Jan 19 2016, 12:08:31) [MSC v.1500 64 bit (AMD64)]
 
 
So ... the broken combinations do not react to any user input. 
'''
from argparse import ArgumentParser

# from gooey  import Gooey, GooeyParser
# git clone https://github.com/chriskiehl/Gooey.git
# python setup.py install

def printVersion():
  import gooey; print "Gooey", gooey.__version__, 
  import wx; print "; wx", wx.__version__, ";",
  import sys; print"Python", sys.version


# @Gooey (monospace_display=True)
def main():
  parser = ArgumentParser(description="Problems with (def=True act=store_true) and (def=False act=store_false).")
  
  # working:
  parser.add_argument("--truefalse",  default=True,  action="store_false", help="default=True  action=store_false")
  parser.add_argument("--falsetrue",  default=False, action="store_true",  help="default=False action=store_true")
  
  # not working:
  parser.add_argument("--truetrue",   default=True,  action="store_true",  help="default=True  action=store_true")
  parser.add_argument("--falsefalse", default=False, action="store_false", help="default=False action=store_false")
  
  # yeah:
  parser.add_argument("--versions",   default=False, action="store_true",  help="print version information")

  args = parser.parse_args()
  print '--truefalse', args.truefalse
  print '--falsetrue', args.falsetrue
  print '--truetrue', args.truetrue
  print '--falsefalse', args.falsefalse
  print

  # print "fine: "       , " ".join(["%5s"%p for p in (A.truefalse, A.falsetrue)]),
  # print "     broken: ", " ".join(["%5s"%p for p in (A.truetrue, A.falsefalse)])
  
  # if A.versions: printVersion()
  
if __name__ == '__main__':
  main()
