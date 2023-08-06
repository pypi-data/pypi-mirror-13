#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

from parser import KParser

def main():

    from optparse import OptionParser

    optparser = OptionParser()
    optparser.add_option('-f','--file',dest="file",type="string",default="",help="Kscript source file")
    optparser.add_option('-o','--out',dest="out",type="string",default="",help="hightlight code HTML file")
    optparser.add_option('-n','--num',dest="keepnum",action="store_true",default=False,help="if keep line numer in html file")

    (opts,args) = optparser.parse_args()

    if opts.file:
        src_file = opts.file
        tks_src = open(opts.file,"r").read()
    else:
        src_file = ""
        tks_src = sys.stdin.read()

    kparser = KParser(src_file,tks_src,opts.keepnum)
    kparser.tks2html()

    if opts.out:
        with open(opts.out,"w") as cout:
            cout.write(kparser.html)
    else:
        print kparser.html

    
if __name__ == "__main__":
    import sys
    sys.exit(main())
