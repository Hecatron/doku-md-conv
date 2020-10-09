#! /usr/bin/env python3

'''
Script for converting dokuwiki to markdown for wikijs
'''

import os
import glob
import os.path as path
from doku_md_conv.wiki_parser import WikiParser
#from doku_md_conv.pandoc_runner import PandocRunner


class DokuMdConv(object):
    '''Class for converting doku to md'''

    def __init__(self):
        self.WikiParser = WikiParser()
        #self.PandocRunner = PandocRunner()
        self.SrcDir = 'D://SourceCode//Local//WikijsSites//original-gbd-src'
        self.DestDir = "D://SourceCode//Hecatron//doku-md-conv//temp1//gbd-dest"
        #self.SrcDir = 'D://SourceCode//Local//WikijsSites//original-bch-src'
        #self.DestDir = "D://SourceCode//Hecatron//doku-md-conv//temp1//bch-dest"

    def main(self):

        file_list = self.get_filelist()
        for srcitem in file_list:
            destitem = self.get_destination(srcitem)
            self.create_destdir(destitem)
            #self.PandocRunner.run(srcitem, destitem)
            self.WikiParser.parse_file(srcitem, destitem)

        print("Done")

    def get_filelist(self):
        '''Get the list of files to parse'''
        searchpath = path.join(self.SrcDir, '**/*.txt')
        ret = glob.glob(searchpath, recursive=True)
        return ret

    def get_destination(self, srcfile):
        '''Get the destination file path from the source file'''
        # Switch around the src / dest path
        ret = path.relpath(srcfile, self.SrcDir)
        ret = path.join(self.DestDir, ret)
        # Switch the extension from .txt to .md
        ret = path.splitext(ret)[0] + '.md'
        return ret

    def create_destdir(self, destfile):
        dirpath = path.dirname(destfile)
        if not path.isdir(dirpath):
            os.makedirs(dirpath)


if __name__ == "__main__":
    DokuMdConv().main()
