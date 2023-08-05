#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from myterm.parser import OptionParser
except:
    from optparse import OptionParser    

try:
    import progressbar
    progress = True
except:
    progess = False

from piwigotools import Piwigo

USAGE = "piwigo verb --param1=value1 --param2=value2"
DESCRIPTION = "my description"
AUTHOR = ""
PROG = ""
VERSION = ""

VERBS = {"upload":
            { 
                "usage" : "usage for verb upload",
                "description" : "description for verb upload",
                "arg" : 
                    {
                        "path" : {"type":"string", "default":"/", "help":"help for path"},
                        "source" : {"type":"string", "default":".", "help":"help for source"}
                            
                    },
            },
        }

def add_dynamic_option(parser):
    # add arg for verb
    verb = sys.argv[1]
    arg_know = ['--help']
    for arg in VERBS.get(sys.argv[1], {'arg':{}})['arg']:
        kw = VERBS[sys.argv[1]]['arg'][arg]
        kw['dest'] = arg
        parser.add_option("--%s" % arg, **kw)
        arg_know.append("--%s" % arg)
    # add arg in argv
    for arg in sys.argv[2:]:
        if arg[:2] == '--' and arg not in arg_know:
            arg = arg[2:].split('=')[0]
            parser.add_option("--%s" % arg , dest=arg, type="string")
            arg_know.append("--%s" % arg)

    #check verb
    if verb not in VERBS:
        parser.print_help()
        parser.error('verb "%s" unknow' % verb)
    
    if '--help' in sys.argv[1:]:
        parser.set_usage(VERBS[verb]["usage"])
        parser.description = VERBS[verb]["description"]
        parser.print_help()
        sys.exit(0)
    
    

def main():
    usage = USAGE
    parser = OptionParser(version="%s %s" % (PROG,VERSION), usage=usage)
    parser.description= DESCRIPTION
    parser.epilog = AUTHOR
    try:
       add_dynamic_option(parser)
       (options, args) = parser.parse_args()
       print(options, args)
    except Exception as e:
        parser.error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
