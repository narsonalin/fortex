#!/usr/bin/env python3
# coding: utf-8

# Code d'Evolution Stellaire, Adaptatif et Modulaire for the 2020 decade.
# Copyright (c) 1997-2023 The Cesam2k20 authors
# SPDX-License-Identifier : GPL-3.0-or-later


import argparse

from CAutoGenF import CAutoGenF

parser = argparse.ArgumentParser()
parser.add_argument('list', type=str, default=None, help='file name with list of files' )

#array to save all the comments with the form !?+letter 
comment=[]

if __name__ == '__main__':

    args = parser.parse_args()

    with open( args.list, 'r' ) as f:
        files = f.readlines()

    path = files[0].replace( '\n', '')

    for file in files[1:]:
        if file[0][0] != '#':
            file = file.split( )
            if len( file ) == 7:
                doc = CAutoGenF( file[0], out=file[1], path=path, depth=int(file[2]), ttype=bool(int(file[3])),
                    write_vars=bool(int(file[4])), pprog=bool(int(file[5])), all_var=bool(int(file[6])) )
                doc.parse()
                doc.write_latex( )

            #for saving all the comments 
            f=open(path+"/"+file[0])
            i=0
            for k in f.readlines():
                i+=1
                if '!?' in k : 
                    comment.append([file[0],str(i),k])
            f.close()
    
    #for printing all the comments in a latex file with name of the file, category, nb line and the content of these comments
    f=open("comments.tex",'w')
    list_sec=[ "!?I : Issues","!?M : Method","!?C : Code"]

    f.write(r"\chapter{Comments}"+'\n')
    f.write(r"Here will be store all the comments in the different files of the code with the code !?."+'\n')

    for i in list_sec : 
        f.write(r"\section{"+i+r'}'+'\n')
        for k in comment:
            if i[0:3] in k[2]:
                f.write(r'\begin{Verbatim}[commandchars=\\\{\},breaklines=true]'+'\n') 
                f.write('\t'+r'\textcolor{purple}{'+k[0]+r'}:\textcolor{blue}{'+k[1]+r'}:'+k[2])
                f.write(r'\end{Verbatim}'+'\n')

    f.close()


        
