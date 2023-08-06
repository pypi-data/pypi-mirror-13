# coding: utf-8

"""GirlFriend需要很多第三方的代码支持，比如自定义的插件、工作流等等，
这些第三方的代码和项目往往都是固定的格式，因此完全可以通过填充模板的方式来减少工作量。
gf_gen就是这种根据据设定好的模板生成代码和项目结构的工具。
"""

import sys
import imp
import os
import os.path
import argparse
from girlfriend.util import script, cmdargs
from girlfriend.exception import GirlFriendBizException


def main():
    args, tpl_arg_list = parse_arguments()
    if not args.template:
        script.show_msg_and_exit(u"必须使用-t参数指定一个模板名称", "yellow")
    template_module = load_template(args.template)
    if template_module is None:
        script.show_msg_and_exit(u"找不到模板 '{}'".format(args.template))
    if not hasattr(template_module, "gen"):
        script.show_msg_and_exit(u"模板模块中必须包含一个gen函数")
    tpl_args = {}  # 执行模板生成所需要的参数
    tpl_parser = getattr(template_module, "parser", None)

    # 显示参数说明
    if args.show_args:
        if tpl_parser is not None:
            print u"模板 '{}' 的参数说明：".format(args.template)
            cmdargs.print_help(tpl_parser)
            exit(0)
        else:
            print u"模板 '{}' 不需要参数。".format(args.template)
            exit(0)

    if tpl_parser:
        tpl_args, _ = tpl_parser.parse_known_args(tpl_arg_list)
        tpl_args = tpl_args.__dict__

    try:
        template_module.gen(path=args.path, **tpl_args)
    except GirlFriendBizException as biz_e:
        script.show_msg_and_exit(unicode(biz_e))
    except Exception:
        script.show_traceback_and_exit()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=__doc__.decode("utf-8"))
    parser.add_argument("-t", dest="template", help=u"使用的模板名称")
    parser.add_argument("-p", dest="path", default=os.getcwd(),
                        help=u"生成项目的路径，默认为当前路径")
    parser.add_argument("--show-args", dest="show_args",
                        action="store_true", help=u"是否显示模板参数的解释")
    ns, tpl_args = parser.parse_known_args(sys.argv[1:])
    return ns, tpl_args


def load_template(template_name):
    file_name = template_name

    # 将点号转换为文件路径分隔符
    if "." in file_name:
        file_name = os.path.join(*file_name.split("."))

    if not file_name.endswith(".py"):
        file_name += ".py"

    # 组成完整的文件路径
    template_path = os.path.join(
        os.environ["HOME"], ".gf/project_templates", file_name)

    if not os.path.exists(template_path):
        return None
    return imp.load_source(template_name, template_path)

if __name__ == "__main__":
    main()
