#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''format:    
    
    python filename version number cumulative or not.
    
    example :python homework1.py v4.4 10 --c=c
'''

import matplotlib.pyplot as plt

import re, sys
from subprocess import Popen, DEVNULL, PIPE
from argparse import ArgumentParser

class ContentException(BaseException):
    def __str__(self):
        error = 'Please check if the argument is appropriate.'
        return error
    
class GetGitLog:
    def __init__(self):
        # Set the arguments required for the class.
        parser = ArgumentParser(description="parse")
        parser.add_argument('revision', help='the vision we want to count.')
        parser.add_argument('rev_range', type=str, help='how many sublevels we want to count')
        parser.add_argument('-c', '--cumulative', type=str, help='whether we chose cumulative or not.')
        args = parser.parse_args()
        self.basetime = 1452466892
        #Passing arguments in a class
        self.rev = args.revision
        try:
            rev_range = int(args.rev_range)
        except (ValueError, UnboundLocalError):
            err = 'Please let -r be a integer.'
            print(err)
        if args.cumulative == "c":
            cumulative = 1
        else:
            cumulative = 0
            print("Dont know what you mean with %s" % args.cumulative)
            sys.exit(-1)
            
            
        self.get_log(cumulative, rev_range)
    
    
    
    
    def get_commit_cnt(self, git_cmd):
        try:
            raw_counts = git_cmd.communicate()[0]
            if raw_counts == 0:
               raise ContentException
        except ContentException as err:
            print(err)
            sys.exit(2)
            # if we request something that does not exist -> 0
        else:
            cnt = re.findall('[0-9]*-[0-9]*-[0-9]*', str(raw_counts))
            return len(cnt)

    def get_tag_days(self, git_cmd, base):
       try:
           seconds = git_cmd.communicate()[0]
           SecPerHour = 3600
           if seconds == 0:
               raise ContentException
       except ContentException as err:
           print(err)
           sys.exit(2)
       return (int(seconds)-base)//SecPerHour
   
    def get_log(self, cumulative, rev_range):
        # setup and fill in the table
        #print("#sublevel commits %s stable fixes" % self.rev)
        #print("lv hour bugs") #tag for R data.frame
        rev1 = self.rev
        
        # base time of v4.1 and v4.4 as ref base
        # fix this to extract the time of the base commit from git !
        # hofrat@Debian:~/git/linux-stable$ git log -1 --pretty=format:"%ct" v4.4
        # 1452466892
        #
        self.sublevels ,self.release_days,self.commits =[],[],[]
        for sl in range(1,rev_range+1):
            rev2 = self.rev + "." + str(sl)
            gitcnt = "git rev-list --pretty=format:\"%ai\" " + rev1 + "..." + rev2
            gittag = "git log -1 --pretty=format:\"%ct\" " + rev2
            #print(gitcnt)
            git_rev_list = Popen(gitcnt, stdout=PIPE, stderr=DEVNULL, shell=True)# grap it
            #print(git_rev_list)
            commit_cnt = self.get_commit_cnt(git_rev_list)# grap it
            #print(commit_cnt)
            if cumulative == 0:
                rev1 = rev2
            # if get back 0 then its an invalid revision number
            #print(commit_cnt)
            if commit_cnt:
                git_tag_date = Popen(gittag, stdout=PIPE, stderr=DEVNULL, shell=True)# grap it
                days = self.get_tag_days(git_tag_date, self.basetime) # grap it
                #print("%d %d %d" % (sl,days,commit_cnt))
                self.sublevels.append(sl) 
                self.release_days.append(days) 
                self.commits.append(commit_cnt)
                
                #self.collect.append((sl,days,commit_cnt))# colect them into list
            else:
                break
    def draw(self):
        self.commits = [self.commits[0]]+[self.commits[i]-self.commits[i-1]  for i in range(1,len(self.commits))]
        print(self.sublevels,self.commits)
        plt.scatter(self.sublevels,self.commits,c ='red') 
        plt.title("development of fixes over sublevel") 
        plt.ylabel("kernel sublevel stable release") 
        plt.xlabel("stable fix commits") 
        plt.savefig("1v4.4.png") 
        plt.show()
        plt.bar(self.sublevels,self.commits) 
        plt.title("development of fixes over sublevel") 
        plt.ylabel("kernel sublevel stable release") 
        plt.xlabel("stable fix commits") 
        plt.savefig("2v4.4.png")
        plt.show()
        plt.plot(self.sublevels,self.commits,linestyle = 'solid') 
        plt.title("development of fixes over sublevel") 
        plt.ylabel("kernel sublevel stable release") 
        plt.xlabel("stable fix commits") 
        plt.savefig("3v4.4.png")
        plt.show()
if __name__ == '__main__':
    getlog = GetGitLog()
    getlog.draw()