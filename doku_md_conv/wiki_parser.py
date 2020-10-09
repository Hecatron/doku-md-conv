import os.path as path
from datetime import datetime
from pathlib import Path


class WikiParser(object):
    '''Class wrapper for running pandoc'''

    def __init__(self):
        self.SrcFile = None
        self.DestFile = None
        self.Contents = None
        self.PageTitle = ''
        self.IsStartFile = False

    def parse_file(self, srcfile, destfile):
        '''Parse a dokuwiki file'''
        self.SrcFile = srcfile
        self.DestFile = destfile

        # Read File
        with open(self.SrcFile) as _file:
            self.Contents = _file.read().splitlines()

        if self.SrcFile.endswith('start.txt'):
            self.IsStartFile = True
        else:
            self.IsStartFile = False

        # Parse File
        self.parse_titles()
        self.addmd_headers()
        self.parse_codeblock()
        self.parse_linefeed()
        self.parse_tables()
        self.parse_links()
        self.parse_wrap()
        self.parse_arrows()
        self.parse_italics()
        self.parse_fontcolor()

        # Write File
        contents = '\n'.join(self.Contents)
        with open(self.DestFile, 'w') as _file:
            _file.write(contents)

    def parse_titles(self):
        '''Convert the headers'''
        for i in range(len(self.Contents)):

            if self.IsStartFile:
                self.parse_title(i, '======', '#')
                self.parse_title(i, '=====', '##')
                self.parse_title(i, '====', '###')
                self.parse_title(i, '===', '####')
                self.parse_title(i, '==', '#####')
            else:

                # For non start pages put the top header into the page title
                line = self.Contents[i]
                if line.startswith('======') and line.endswith('======'):
                    line = line.replace('======', '')
                    self.PageTitle = line.rstrip(' ').lstrip(' ')
                    self.Contents[i] = ''
                    continue

                self.parse_title(i, '=====', '#')
                self.parse_title(i, '====', '##')
                self.parse_title(i, '===', '###')
                self.parse_title(i, '==', '####')

    def parse_title(self, index, doku_title, md_title):
        line = self.Contents[index]
        if line.startswith(doku_title) and line.endswith(doku_title):
            line = line.replace(doku_title, '')
            self.Contents[index] = md_title + line.rstrip(' ')

    def addmd_headers(self):
        '''Add headers'''
        now = datetime.now()
        dttm = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        # FIXME Override for git import
        dttm = '2020-10-07T23:07:00.000Z'

        title = self.PageTitle
        if self.IsStartFile:
            title = 'start'

        header = ['---']
        header += ['title: ' + title]
        header += ['description: ']
        header += ['published: true']
        header += ['date: ' + dttm]
        header += ['tags: ']
        header += ['editor: undefined']
        header += ['dateCreated: ' + dttm]
        header += ['---']
        header += self.Contents
        self.Contents = header

    def parse_codeblock(self):
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            if '<code>' in line:
                self.Contents[i] = line.replace('<code>', "```")
                continue
            if '</code>' in line:
                self.Contents[i] = line.replace('</code>', "```")
                continue
            if '<sxh>' in line:
                self.Contents[i] = line.replace('<sxh>', "```")
                continue
            if '</sxh>' in line:
                self.Contents[i] = line.replace('</sxh>', "```")
                continue
            if '<sxh ' in line:
                line = line.replace('<sxh', '').replace('>', '')
                self.Contents[i] = "```" + line
                continue
            if '<code ' in line:
                line = line.replace('<code', '').replace('>', '')
                self.Contents[i] = "```" + line
                continue

    def parse_linefeed(self):
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            if '\\\\' in line:
                self.Contents[i] = line.replace('\\\\', "<br>")
                continue

    def parse_tables(self):
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            if line.startswith('^') and line.endswith('^'):
                postline = ''
                # Create a separator line
                for item in line:
                    if item == '^':
                        postline += '|'
                    else:
                        postline += '-'
                line = line.replace('^', '|')
                line += '\n' + postline
                self.Contents[i] = line

    def parse_links(self):
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            # Parse page links
            while '[[' in line:
                startpos = line.find('[[')
                endpos = line.find(']]')
                if startpos == -1 or endpos == -1:
                    break
                linkstr = self.parse_page_link(line[startpos:endpos + 2])
                line = line[:startpos] + linkstr + line[endpos + 2:]
                self.Contents[i] = line
            # Parse media links
            while '{{' in line:
                startpos = line.find('{{')
                endpos = line.find('}}')
                if startpos == -1 or endpos == -1:
                    break
                linkstr = self.parse_media_link(line[startpos:endpos + 2])
                line = line[:startpos] + linkstr + line[endpos + 2:]
                self.Contents[i] = line

    def parse_page_link(self, link_item):
        link_item = link_item.replace('[[', '').replace(']]', '')
        link_arr = link_item.split('|')
        dest = link_arr[0]
        dest = dest.replace(':', '/')
        dest = dest.replace('http/', 'http:').replace('https/', 'https:')
        if not (dest.startswith('http:') or dest.startswith('https:')):

            # Make sure relative links work inside github / git
            if not dest.endswith('.md'):
                dest += '.md'

        description = ''
        if len(link_arr) > 1:
            description = link_arr[1]
        else:
            if dest.startswith('http://') or dest.startswith('https://'):
                description = dest
            else:
                description = path.basename(dest)
        ret = '[' + description + ']' + '(' + dest + ')'
        return ret

    def parse_media_link(self, link_item):
        link_item = link_item.replace('{{', '').replace('}}', '')
        link_arr = link_item.split('|')
        dest = link_arr[0]
        dest = dest.replace(':', '/')

        imgsize = None
        tmp1 = dest.split('?')
        if len(tmp1) > 1:
            dest = tmp1[0]
            imgsize = '=' + tmp1[1] + 'x'

        description = ''
        if len(link_arr) > 1:
            description = link_arr[1]
            if description == '':
                description = path.basename(dest)
        else:
            description = path.basename(dest)

        ret = ''
        if imgsize:
            ret = '![' + description + ']' + '(' + dest + ' ' + imgsize + ')'
        else:
            ret = '![' + description + ']' + '(' + dest + ')'
        return ret

    def parse_wrap(self):
        '''Parse wrap statements'''
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            if '<wrap em>' in line:
                line = line.replace('<wrap em>', '<em>').replace('</wrap>', '</em>')
            if '<wrap lo>' in line:
                line = line.replace('<wrap lo>', '<em>').replace('</wrap>', '</em>')
            self.Contents[i] = line

        wrap_type = 'info'
        inside_wrap_blk = False
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            if '</WRAP>' in line or '</wrap>' in line:
                inside_wrap_blk = False
                line = '{.is-' + wrap_type + '}'
                self.Contents[i] = line
                wrap_type = 'info'
                continue
            if '<WRAP' in line or '<wrap' in line:
                inside_wrap_blk = True
                if 'important' in line:
                    wrap_type = 'warning'
                if 'alert' in line:
                    wrap_type = 'danger'
                self.Contents[i] = ''
                continue
            if inside_wrap_blk:
                line = '> ' + line
                self.Contents[i] = line

    def parse_arrows(self):
        '''Parse wrap statements'''
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            #if 'Browse to Computer Configuration' in line:
            #    if r'â†’' in line:
            #        print('test')

            if r'â†’' in line:
                line = line.replace(r'â†’', '->')
                self.Contents[i] = line

    def parse_italics(self):
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            if 'http://' in line or 'https://' in line:
                continue
            while line.count('//') > 1:
                line = line.replace('//', '<em>', 1)
                line = line.replace('//', '</em>', 1)
            self.Contents[i] = line

    def parse_fontcolor(self):
        for i in range(len(self.Contents)):
            line = self.Contents[i]
            if '</fc>' in line or '<fc #FF0000>' in line:
                line = line.replace('<fc #FF0000>', '<span style="color:red">')
                line = line.replace('</fc>', '</span>')
                self.Contents[i] = line
