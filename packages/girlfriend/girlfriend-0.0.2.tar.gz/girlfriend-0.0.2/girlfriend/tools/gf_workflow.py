# coding: utf-8

"""使用此工具，可以直接通过命令行来执行一个工作流！
"""

import sys
import argparse
import functools
from girlfriend.exception import InvalidArgumentException


class WorkflowTask(object):

    """该类用于组装提交给执行引擎的工作流描述
    """

    @classmethod
    def wrap_module(cls, task_module):
        """将一个模块包装成WorkflowTask对象
        """

        # 嗯，只有workflow一个是必须的
        if not hasattr(task_module, "workflow"):
            raise InvalidArgumentException(u"模块缺少workflow变量")

        _getattr = functools.partial(getattr, task_module)
        return cls(
            workflow=_getattr("workflow"),
            env_list=_getattr("env_list", tuple()),
            args=_getattr("args", {}),
            listeners=_getattr("listeners", tuple()),
            config_file=_getattr("config_file", ""),
            register_arguments=_getattr("register_arguments"),
            parse_arguments=_getattr("parse_arguments")
        )

    def __init__(self, workflow, env_list, args, listeners,
                 config_file, register_arguments, parse_arguments):
        """
            :param env_list 环境描述对象列表
            :param workflow 工作流单元列表
            :param args 参数
            :param listeners 监听器列表
            :param config_file 配置文件
            :param register_arguments 注册参数解析逻辑
        """
        self.workflow = workflow
        self.env_list = env_list
        self.args = args
        self.listeners = listeners
        self.config_file = config_file
        self.register_arguments = register_arguments
        self.parse_arguments = parse_arguments


class Env(object):

    """工作环境，在实践中，不同的工作流往往会工作在不同的场景之中
       Env对象提供了对不同场景的描述，允许工作流在不同的场景中使用不同的参数和配置文件
    """

    def __init__(self, name, args, config_file, description):
        """
            :param name 工作环境名称
            :param args 专属此环境的参数
            :param config_file 配置文件
            :param description 工作环境描述
        """
        self.name = name
        self.args = args
        self.config_file = config_file
        self.description = description


def main():
    print "gf workflow"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="test")

    parser.add_argument('-a', action="store", dest="a")
    parser.add_argument("-b", action="store", dest="b")

    ns = parser.parse_known_args(sys.argv[1:])
    print ns

    parser.add_argument("-c", action="store", dest="c")
    ns = parser.parse_known_args(sys.argv[1:])
    print ns
