# coding: utf-8

"""内置模板集中处
"""

TEMPLATE_TEMPLATE = """
# coding: utf-8

\"\"\"生成模板的模板
\"\"\"

import argparse
from girlfriend.util import file_template, script

parser = argparse.ArgumentParser(description=__doc__.decode("utf-8"))
parser.add_argument("-n", dest="name",
                    action="store", help=u"模板名称")


CONTENT = \"\"\"
# coding: utf-8

\\"\\"\\"
Docs goes here
\\"\\"\\"

import argparse
from girlfriend.util.file_template import Dir, File
from girlfriend.util.script import (
    show_traceback_and_exit,
    show_msg_and_exit
)

parser = argparse.ArgumentParser(description=__doc__.decode("utf-8"))
parser.add_argument("--n", dest="name",
                    action="store", help=u"模板名称")


def gen(path, name):
    pass
\"\"\"


def gen(name, path):
    if not name:
        script.show_msg_and_exit(u"必须使用-n参数来指定模板文件名")
    if not name.endswith(".py"):
        name += ".py"
    file_template.File(name, content=CONTENT).makeme(path)
"""
