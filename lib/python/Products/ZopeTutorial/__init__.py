##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
import TutorialTopic
import App.Common
import os.path
import string
import os
import stat
from DateTime import DateTime
from urllib import quote_plus
from cgi import escape
import re
from HelpSys import APIHelpTopic


def initialize(context):
    # abuse registerClass to get a tutorial constructor
    # in the product add list
    context.registerClass(
        None,
        meta_type='Zope Tutorial',
        constructors=(TutorialTopic.addTutorialForm, TutorialTopic.addTutorial),
        )

    # create tutorial help topics
    lesson_path=os.path.join(App.Common.package_home(globals()), 'tutorial.stx')
    glossary_path=os.path.join(App.Common.package_home(globals()), 'glossary.stx')
    help=context.getProductHelp()

    # test to see if nothing has changed since last registration
    if help.lastRegistered is not None and \
            help.lastRegistered >= DateTime(os.stat(lesson_path)[stat.ST_MTIME]):
        return
    help.lastRegistered=DateTime()
    
    # delete old help topics
    for id in help.objectIds('Help Topic'):
        help._delObject(id)
    
    # create glossary
    text=open(glossary_path).read()
    text=term_pat.sub(defineTerm, text)
    glossary=TutorialTopic.TutorialTopic('tutorialGlossary', 'Zope Tutorial Glossary', text)
    context.registerHelpTopic('tutorialGlossary', glossary)

    # create lessons
    f=open(lesson_path)
    lines=[]
    id=0
    
    while 1:
        line = f.readline()
        if (string.strip(line) and string.find(line, ' ') != 0) or line=='':
            # new topic
            if lines:
                id = id + 1
                topic_id = 'topic_%02d' % id
                text=string.join(lines[1:], '')
                text=term_pat.sub(glossaryTerm, text)
                topic=TutorialTopic.TutorialTopic(topic_id, string.strip(lines[0]), spacestrip(text))
                context.registerHelpTopic(topic_id, topic)            
            lines=[line]
        else:
            lines.append(line)
        if line == '':
            break
    f.close()


def spacestrip(txt):
    """ dedent text by 2 spaces !

    We need this to workaround a nasty bug in STXNG. 
    STXNG creates empty <pre>..</pre> when then text start
    if a level > 1
    """
    
    l = []
    for x in string.split(txt,"\n"):
        if len(x)>2 and x[:2]=='  ':
            l.append(x[2:])

    return string.join(l,'\n')


# Glossary functions
# ----------------

term_pat=re.compile(r'\[([^\]])+?\]')
terms=[]

def glossaryTerm(match):
    """
    A linked glossary term
    """
    name=match.group(1)
    if name in terms:
        return """<a href="../tutorialGlossary#%s">%s</a>""" % \
                (quote_plus(name), escape(name))
    return """[%s]""" % name

def defineTerm(match):
    """
    Define a glossary term
    """
    name=match.group(1)
    terms.append(name)
    return """<a name="%s"></a>\n\n<strong>%s</strong>""" % \
            (quote_plus(name), escape(name))
