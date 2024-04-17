#!/usr/bin/env python3
# coding: utf-8

# Code d'Evolution Stellaire, Adaptatif et Modulaire for the 2020 decade.
# Copyright (c) 1997-2023 The Cesam2k20 authors
# SPDX-License-Identifier : GPL-3.0-or-later


import numpy as np
import re

NO_COLOR  = "\033[0m"
GREEN     = "\033[32;01m"

class CAGError( Exception ):
    __module__ = 'CAutoGenF'

    def __init__( self, message ):
        self.message = message
        super().__init__( self.message )

types = ['real', 'double', 'complex', 'integer', 'character', 'type', 'logical', 'class']
procs  = ['subroutine', 'function']#, 'program']# , 'type']

class CAutoGenF( ):

    all_variables = {"mod_kind", "mod_communicate", "submod_error", "mod_hdf5_utils", "slatec",
        "mod_donnees", "mod_numerique", "submod_num_saha", "mod_variables", "z14xcotrin21", "mod_opa",
        "submod_opa_compton", "submod_opa_compton_Poutanen", "submod_opa_int_zsx", "submod_opa_gong",
        "submod_opa_yveline_lisse", "submod_opa_opalCO", "submod_opa_opal2", "submod_opa_yveline",
        "submod_opa_kappa_cond", "submod_opa_yveline_daniel", "submod_opa_mono_OP",
        "submod_opa_cond_yveline", "submod_opa_cond_yveline21", "submod_opa_houdek9",
        "submod_opa_smooth", "mod_etat", "submod_etat_gong", "submod_etat_ceff", "submod_etat_eff",
        "submod_etat_mhd", "submod_etat_opal5Z", "submod_etat_saha", "mod_conv", "mod_nuc", "mod_thermo",
        "mod_atm", "mod_alecian", "mod_evol", "submod_evol2d", "mod_static", "mod_cesam", "mod_exploit"}

    def __init__( self, name, path='.', out='out.tex', depth=1, ttype=False, pprog=False, write_vars=True ):
        self.path       = path
        self.name       = name
        self.out        = out
        self.depth      = depth
        # self.type is True if the given file defines a type.
        self.type       = ttype
        # self.prog is True if the given file defines a program.
        self.prog       = pprog
        # If False, don't write the documentation for the arguments
        self.write_vars = write_vars

    def __deal_with_var_decl( self, line, vari, parent, init_dict=None ):
        _dict = self.dict[parent] if init_dict is None else init_dict
        words2 = line.replace('\n', '').split( sep='!' )
        if words2[0][-1] != '&':
            in_var_decl = False
            _dict['vars'][vari]['decl'].append( words2[0].strip( ) )
        else:
            in_var_decl = True
            _dict['vars'][vari]['decl'].append( words2[0][:-1].strip( ) )
        return in_var_decl

    def __deal_with_proc_decl( self, i, line, parent, new_decl=False ):#, init_dict=None ):
        # First look if the procedure name was find in a format, print or write statement
        line_tmp = line.replace( '(', ' ').replace( ',', ' ').replace( '*', ' ')
        words1 = line_tmp.split( )
        if self.__is_in_list( ['format', 'print', 'write'], words1[:2]):
            return None, parent
        words2 = line.replace('\n', '').split( sep='!' )


        if 'end' in words2[0]:
            in_proc_decl = False
            parent       = ''
        elif words2[0][-1] == '&':
            in_proc_decl = True
            if not parent:
                parent = f"{i:05d}"
                self.vari = -1
            if parent not in list( self.dict.keys() ):
                self.dict[parent] = {'doc' : [], 'proc' : [], 'vars' : []}
            self.dict[parent]['proc'].append( words2[0][:-1].strip( ) )
        else:
            in_proc_decl = False
            if not parent:
                parent = f"{i:05d}"
                self.vari = -1
            if parent not in list( self.dict.keys() ):
                self.dict[parent] = {'doc' : [], 'proc' : [], 'vars' : []}
            self.dict[parent]['proc'].append( words2[0].strip( ) )
        return in_proc_decl, parent

    def __is_in_list( self, list1, list2, out=False):
        for elem in list1:
            if elem in list2:
                if out:
                    return True, elem
                else:
                    return True
        if out:
            return False, None
        else:
            return False

    def __capitalize( self, string):
        string = re.sub( "(^|[.?!])\s*([a-zA-Z])", lambda p: p.group(0).upper(), string )
        string = string.replace( 'e.G.', 'e.g.' )
        string = string.replace( '.F', '.f' )
        return string

    def __process_docstring( self, lines ):
        core        = ['']
        references  = {}
        history     = {}
        orig_author = {}
        advisor     = {}

        in_bools = {'reference':False, 'history':False, 'orig_author':False, 'advisor':False}

        for line in lines:
            words = line.split()
            if len(words) == 0:
                if not np.array( list( in_bools.values() ) ).any():
                    core.append( '\n' )
                    core.append( '' )

            elif ':' in [words[0], words[0][0]]:
                if words[0] == ':':
                    arg = words[1].replace(':', '')
                    words = words[2:]
                else:
                    arg = words[0][1:].replace(':', '')
                    words = words[1:]

                if arg == 'reference':
                    name = words[0].replace(':', '').strip()

                    if len( words ) == 1:
                        raise CAGError( f"{arg} was defined but no description was provided." )
                    elif words[1] == ':':
                        del words[1]

                    if len( words ) > 1:
                        references[name] = ' '.join( words[1:] )

                elif arg == 'history':
                    name = words[0].replace(':', '').strip()
                    if len( words ) == 1:
                        raise CAGError( f"{arg} was defined but no description was provided." )
                    elif words[1] == ':':
                        del words[1]

                    if len( words ) > 1:
                        history[name] = ' '.join( words[1:] )

                elif arg == 'author':
                    name = f"{np.random.randint(2**30, size=1)[0]:8X}"
                    if len( words ) == 1:
                        raise CAGError( f"{arg} was defined but no description was provided." )
                    elif words[0] == ':':
                        del words[0]

                    if len( words ) > 1:
                        orig_author[name] = ' '.join( words )

                elif arg == 'advisor':
                    name = f"{np.random.randint(2**30, size=1)[0]:8X}"
                    if len( words ) == 1:
                        raise CAGError( f"{arg} was defined but no description was provided." )
                    elif words[0] == ':':
                        del words[0]

                    if len( words ) > 1:
                        advisor[name] = ' '.join( words )

                in_bools = in_bools.fromkeys( in_bools, False )
                in_bools[arg] = True

            elif in_bools['reference']:
                references[name]       += ' ' + ' '.join( words )
            elif in_bools['history']:
                history[name]          += ' ' + ' '.join( words )
            elif in_bools['orig_author']:
                orig_author[name]          += ' ' + ' '.join( words )
            elif in_bools['advisor']:
                advisor[name]          += ' ' + ' '.join( words )
            else:
                core[-1] += ' ' + ' '.join( words )

        docstring = {
            'core':core,
            'references':references,
            'history': history,
            'orig_author': orig_author,
            'advisor': advisor}

        return docstring

    def __get_default( self, var ):
        """
        Seperate the name of the variable and its default value if initialized in line.
        """
        if '=' in var:
            i = var.index('=')
            return [var[:i], var[i:]]
        else:
            return [var, '']

    def __write_var( self, var ):
        decl = ''.join(var['decl'])
        if 'intent' not in decl and not (self.type or self.prog): return None, None, None

        doc  = var['doc']
        decl = decl.split( sep='::' )
        vrs  = self.__get_default( decl[1].strip() )
        decl = decl[0].strip( )
        decl = decl.replace('l (', 'l(').replace('s (', 's(').replace('e (', 'e(')

        return vrs, decl, '\n'.join( doc )

    def parse( self ):
        print(f"Parsing {self.path}/{self.name}...", end='')
        with open( self.path+'/'+self.name ) as f:
            lines = f.readlines()

        if self.type:
            self.dict    = {'':{'doc' : [], 'proc' : [], 'vars' : []}}
        elif self.prog:
            self.dict    = {'':{'doc' : [], 'proc' : [], 'vars' : []}}
        else:
            self.dict    = {}
        self.init_dict    = {'doc' : [], 'proc' : [], 'vars' : []}
        new_lines    = []
        var_doc      = []
        parent       = ''
        in_var_doc   = False
        in_var_decl  = False
        in_proc_decl = False
        self.vari         = -1
        for i, line in enumerate( lines ):
            words = line.split( )

            if len( words ) > 1 :
                if len( words[0] ) > 1:
                    if words[0][0] == '!':
                        if words[0][1] == '!':
                            # in description
                            words[0] = words[0][2:]
                            if parent or self.type or self.prog:
                                self.dict[parent]['doc'].append( ' '.join( words ) )
                            #else:
                            #    self.init_dict['doc'].append( ' '.join( words ) )
                        elif words[0][1] == '>':
                            # in variable description
                            words[0] = words[0][2:]
                            if in_var_doc:
                                var_doc.append( ' '.join( words ) )
                            else:
                                in_var_doc = True
                                var_doc    = [' '.join( words )]
                    else:
                        if words[0].lower() == 'contains':
                            break
                        if self.__is_in_list( procs, words ):
                            in_proc_decl_tmp, parent = self.__deal_with_proc_decl( i, line, parent,
                                new_decl=True)#, init_dict=self.init_dict )
                            in_proc_decl = False if in_proc_decl_tmp is None else in_proc_decl_tmp

                        elif in_proc_decl:
                            in_proc_decl_tmp, parent = self.__deal_with_proc_decl( i, line, parent )
                            in_proc_decl = False if in_proc_decl_tmp is None else in_proc_decl_tmp

                        elif words[0].split(sep='(')[0].split( sep=',' )[0] in types:
                            in_var_doc  = False
                            self.vari += 1
                            if parent or self.type or self.prog:
                                self.dict[parent]['vars'].append( {'decl':[], 'doc':var_doc} )
                            in_var_decl = self.__deal_with_var_decl( line, self.vari, parent )

                        elif in_var_decl:
                            in_var_decl = self.__deal_with_var_decl( line, self.vari, parent )


                        elif in_proc_decl:
                            in_proc_decl, parent = self.__deal_with_proc_decl( i, line, parent )
            if len( words ) == 1:
                if words[0].lower() == 'contains':
                            break
                if words[0] == '!!':
                    if parent or self.type or self.prog:
                        self.dict[parent]['doc'].append( ' ' )
                    #else:
                    #    self.init_dict['doc'].append( ' ' )
                elif words[0] == '!>':
                    if in_var_doc:
                        var_doc[-1] += '\\\\'
                        #var_doc.append( ' ' )
                    else:
                        in_var_doc = True
                        var_doc    = [' ']

    def __clean_underscores2( self, text ):
        stext = text.strip()
        if len(stext):
            add = 1
            ltext = stext.split( sep='`' )

            n = len( ltext ) // 2 + 1 - add
            for i in range( n ):
                ltext[2*i+add] = '\\code{' + ltext[2*i+add] + '}'

            text = ' '.join( ltext )

            text = text.replace( ' .', '.').replace( ' ,', ',')

        return text

    def __bold_font( self, text ):
        stext = text.strip()
        if len(stext):
            add = 1
            ltext = stext.split( sep='#' )

            n = len( ltext ) // 2 + 1 - add
            for i in range( n ):
                ltext[2*i+add] = '\\textbf{' + ltext[2*i+add] + '}'

            text = ' '.join( ltext )

            text = text.replace( ' .', '.').replace( ' ,', ',')

        return text

    def __point( self, text ):
        stext = text.strip()
        if len( stext ) == 0: return stext
        if stext[-1] not in ['.', '!', '?']: return stext + '.'
        return stext

    def clean_underscores( self, text ):

        ltext = text.split( sep='$' )
        n = len( ltext ) // 2 + 1
        for i in range( n ):
            ltext[2*i] = self.__clean_underscores2( ltext[2*i] )
        return r'\xspace$\xspace '.join( ltext )

    def write_proc_latex( self, text ):
        if not (self.type or self.prog):
            for parent in list( self.dict.keys() ):
                proc_line = ''.join( self.dict[parent]['proc'] )
                _, elem = self.__is_in_list( procs, proc_line, out=True )
                # get everything after proc type:
                proc_name = proc_line.split( sep=elem )[-1]
                # get everything before arguments (i.e. proc name):
                proc_name = proc_name.split( sep='(' )[0]
                # remove spaces
                proc_name = proc_name.strip( )

                if self.depth == 1:
                    sect = 'subsection'
                elif self.depth == 2:
                    sect = 'subsubsection'
                text += "\n\\%s{%s \\ifo{%s}}\n\n" % (sect, self.__capitalize(elem), proc_name)
                text += "\\label{%s:%s}\\index{\\code{%s}}\n\n" % (sect, proc_name, self.name)

                text += '\\begin{minted}[bgcolor=codebg,linenos=false]{fortran}\n'
                text += proc_line + '\n'
                text += '\\end{minted}\n\n'


                doc = self.__process_docstring( self.dict[parent]['doc'] )
                text += self.write_doc_var_latex( doc, self.dict[parent]['vars'] )
        else:
            doc = self.__process_docstring( self.dict['']['doc'] )
            text += self.write_doc_var_latex( doc, self.dict['']['vars'] )


        return text

    def write_doc_var_latex( self, docstring, vvars ):
        text = ''
        if any(c for c in docstring['core']):
            for parag in docstring['core']:
                text += self.__bold_font( self.clean_underscores( parag ) ) + '\n'
            text += '\n'

        text = self.__capitalize( text )

        desc = False

        args = False

        if not self.write_vars:
            text2  = "    \\item{\\textsf{\\textbf{Arguments}}}:\n"
            text2  += "        Same as generic subroutine\n"
        else:
            if (self.type or self.prog) and len( vvars ):

                # name of the type
                vv, decl, doc = self.__write_var( vvars[0] )
                vv, default   = vv
                doc = self.__bold_font( self.__point( doc ) )
                if default:
                    doc += r" Initial value: \code{" + f"{vv}{default}" + r"}."
                text2  = "\\code{%s}: \\ifo{%s} \n\n" % (vv, decl )
                if not desc:
                    text2 += "\\begin{description}\n"
                    desc = True
                text2 += "    \\item{\\textsf{\\textbf{Members}}}:\n"
                text2 += "    \\begin{description}\n"
                for v in vvars[1:]:
                    vv, decl, doc = self.__write_var( v )
                    if vv is not None:
                        doc = self.__bold_font( self.__point( doc ) )
                        vv, default   = vv
                        if default:
                            doc += r" Initial value: \code{" + f"{vv}{default}" + r"}."
                        args = True
                        if not desc:
                            text += "\\begin{description}\n"
                            desc = True
                        descr = self.__bold_font( self.__point( self.__capitalize( self.clean_underscores( doc ) ) ) if doc else '' )
                        text2 += "        \\item[\\code{%s}]: \\ifo{%s} \\\\\n \t\t\t %s\n" % (vv, decl, descr )
                text2 += "    \\end{description}\n\n"

            else:
                text2  = "    \\item{\\textsf{\\textbf{Arguments}}}:\n"
                text2 += "    \\begin{description}\n"
                for v in vvars:
                    vv, decl, doc = self.__write_var( v )
                    if vv is not None:
                        doc = self.__bold_font( self.__point( doc ) )
                        vv, default   = vv
                        if default:
                            doc += r" Initial value: \code{" + f"{vv}{default}" + r"}."
                        args = True
                        if not desc:
                            text += "\\begin{description}\n"
                            desc = True
                        descr = self.__bold_font( self.__point( self.__capitalize( self.clean_underscores( doc ) ) ) if doc else '' )
                        text2 += "        \\item[\\code{%s}]: \\ifo{%s} \\\\\n \t\t\t %s\n" % (vv, decl, descr )
                text2 += "    \\end{description}\n\n"

        # if arguments is not empty
        if args:
            text +=  text2

        if docstring['references']:
            if not desc:
                text += "\\begin{description}\n"
                desc = True
            text += "    \\item{\\textsf{\\textbf{References}}}:\n"
            text += "    \\begin{description}\n"
            for r in docstring['references']:
                descr = self.__point( self.__capitalize( self.clean_underscores( docstring['references'][r] ) ) )
                text += "        \\item[%s]: %s\n" % (r, descr )
            text += "    \\end{description}\n\n"

        if docstring['history']:
            if not desc:
                text += "\\begin{description}\n"
                desc = True
            text += "    \\item{\\textsf{\\textbf{History}}}:\n"
            text += "    \\begin{description}\n"
            for h in docstring['history']:
                descr = self.__point( self.__capitalize( self.clean_underscores( docstring['history'][h] ) ) )
                text += "        \\item[%s]: %s\n" % (h, descr )
            text += "    \\end{description}\n\n"

        if docstring['orig_author']:
            if not desc:
                text += "\\begin{description}\n"
                desc = True
            text += "    \\item{\\textsf{\\textbf{Orignal author(s)}}}:\n"
            text += "    \\begin{description}\n"
            for oa in docstring['orig_author']:
                descr = self.__point( self.__capitalize( self.clean_underscores( docstring['orig_author'][oa] ) ) )
                text += "        \\item[$\\bullet$] %s\n" % (descr )
            text += "    \\end{description}\n\n"

        if docstring['advisor']:
            if not desc:
                text += "\\begin{description}\n"
                desc = True
            text += "    \\item{\\textsf{\\textbf{Advisor(s)}}}:\n"
            text += "    \\begin{description}\n"
            for a in docstring['advisor']:
                descr = self.__point( self.__capitalize( self.clean_underscores( docstring['advisor'][a] ) ) )
                text += "        \\item[$\\bullet$] %s\n" % (descr )
            text += "    \\end{description}\n\n"

        if desc:
            text += "\\end{description}\n"



        return text.replace('&','\\&').replace('%','\\%')



    def write_latex( self ):
        text = "%!TEX encoding = UTF-8 Unicode\n"

        text = self.write_proc_latex( text )

        with open(self.out, 'w') as f:
            f.write( text )

        print(f"{GREEN}[DONE]{NO_COLOR}")

