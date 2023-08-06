'''The Parser of tks2html

By Leslie Zhu <pythonisland@gmail.com>


'''

import re

from lex import KLexical as klexer

class KParser(object):

    def __init__(self,src_file="",tks_src="",keepnum=False):
        self.title = src_file if src_file else "tks2html: convert kscript into highlight code html file"
        self.tks_src = tks_src
        self.keepnum = keepnum
        self.html = u""

        self.keyword_list = ["parallel","data","args","init","query","load","load0","if","else","for_each","and","merge","join","by","mode","map","lookup","output",
                             "in","xc","term","print","sent","drop","index"]
        self.function_list = ["max","GetCalendarMonth","GetRelativeMonth","num2str","str2num","date"]
        self.comment_list = ["//","/*","*/","#"]
        self.builtin_var_regex = [r"\~\d+",r".*[\@\$]$","\".*\"","_N\d+_"]


    def _header(self):
        self.html += "<html><head><title>%s</title>"  % (self.title)
        self.html += '''<style type=\"text/css\">
    body {
        font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
        background-color: white;
        }
    p {
        margin-left: 20px
        }
    h1 {
        font-size: 2.6em;
        line-height: 1.2em;
        margin-bottom: 0.6667em;
        text-rendering: optimizelegibility;
        font-weight: bold;
        font-family: 'Open Sans', "Helvetica Neue", "Helvetica", "Microsoft YaHei", "WenQuanYi Micro Hei", Arial, sans-serif;
        margin-top: 20px;
        color: inherit
        }
    table {
        background: black;
        color: white;
        padding-right: 15px;
        padding-left: 15px;
        }
    .keyword {
        color: #00ffff;
        font-weight: bold;
        }
    .function {
        color: #87cefa;
        font-weight: bold;
        font-style: italic;
        }
    .butilin-var {
        color: #eedd82;
        font-weight: bold;
        font-style: italic;
        }
    .comment, .comment-str{
        color: #66cdaa;
        font-style: italic;
        }
</style>'''
        self.html += "</head><body><h1>%s</h1><div><table><tbody>" % (self.title)

    def _end(self):
        self.html += "</tbody></table></div></body></html>"

    def tks2html(self):
        self._header()
        self._analyse()
        self._end()

    def _analyse(self):
        content = ""
        i = 0
        for tks_line in self.tks_src.split('\n'):
            i += 1
            if self.keepnum:
                content += "<tr><td><span class='line-num'><b>%s</b></span></td><td><p>" % i
            else:
                content += "<tr><td><p>"

            in_comment = False
            comment_str = ""
            other_str = ""
            for token in klexer(tks_line.rstrip()).analyse():
                if in_comment:
                    comment_str += token
                    continue
                if token in self.keyword_list:
                    content += "<span class='keyword'>%s</span>" % token
                elif token in self.function_list:
                    content += "<span class='function'>%s</span>" % token
                elif token in self.comment_list:
                    content += "<span class='comment'>%s</span>" % token
                    in_comment = True
                elif any(re.search(regex,token) for regex in self.builtin_var_regex):
                    content += "<span class='butilin-var'>%s</span>" % token
                else:
                    content += "%s" % token.replace(' ','&nbsp;').replace('\t','&nbsp;' * 4)

            # for comment
            if in_comment:
                content += "<span class='comment-str'>%s</span>" % comment_str

            content += '</p></td></tr>'

            

        self.html += content
