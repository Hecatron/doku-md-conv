
import subprocess


class PandocRunner(object):
    '''Class wrapper for running pandoc'''

    def __init__(self):
        self.Pandoc = 'pandoc'
        self.WorkingDir = '.'
        self.InFormat = 'dokuwiki'
        self.OutFormat = 'markdown'
        self.AdditionalOpts = ['--atx-headers']

    def run(self, srcfile, destfile):
        '''Run pandoc'''
        cmdarray = [self.Pandoc]
        cmdarray += self.AdditionalOpts
        cmdarray += ['-f', self.InFormat, '-t', self.OutFormat]
        cmdarray += ['-o', destfile, srcfile]
        self.run_cmd(cmdarray)

    def run_cmd(self, cmdarray):
        '''Run a exe / command'''
        proc = subprocess.Popen(cmdarray, cwd=self.WorkingDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        proc_out, proc_err = proc.communicate()
        print(proc_out)
        print(proc_err)
        if proc.returncode != 0:
            raise RuntimeError("Failure to run command")
        return
