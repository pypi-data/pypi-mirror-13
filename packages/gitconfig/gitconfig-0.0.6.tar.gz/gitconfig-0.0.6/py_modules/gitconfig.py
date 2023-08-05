#!/usr/bin/env python
from git.config import GitConfigParser # GitPython dist
from conf import *
from fullpath import *
from public import *

@public
class Gitconfig(Conf):
    read_only = False

    def __init__(self,path,read_only=False):
        self.read_only = read_only
        path = fullpath(path)
        parser = GitConfigParser(path,read_only=self.read_only)
        Conf.__init__(self,path=path,parser=parser)

    def write(self):
        self.parser.write()

gitconfig = Gitconfig("~/.gitconfig",True)
public(gitconfig)

if __name__=="__main__":
    print(gitconfig)
    print("section: %s" % gitconfig.sections)
    print("gitconfig.init.templatedir: %s" % gitconfig.init.templatedir)
    print("not_existing: %s" % gitconfig.not_existing)
