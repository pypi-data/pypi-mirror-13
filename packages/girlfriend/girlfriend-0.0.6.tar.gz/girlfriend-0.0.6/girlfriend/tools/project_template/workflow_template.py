# coding: utf-8

"""工作流模板
"""

import cmd
import types
import argparse
from termcolor import colored
from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty
)


cmd_parser = argparse.ArgumentParser(description=__doc__.decode("utf-8"))
cmd_parser.add_argument("--file-name", "-f", dest="file_name", help=u"工作流文件名称")


class CodeTemplate(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def unit_type(self):
        pass

    @abstractmethod
    def gen_code(self):
        pass

    def __eq__(self, element):
        if isinstance(element, types.StringTypes):
            return element == self.unit_name
        return element.unit_name == self.unit_name


class PluginBasedJobTemplate(CodeTemplate):

    """基于插件的Job模板
    """

    def __init__(self, unit_name, plugin_name=None,
                 auto_imports=None, args_template=None, args_function=None,
                 args_list=None):
        """
        :param unit_name Job名称
        :param plugin_name 插件名称
        :param auto_imports 自动导入列表
        :param args_template 参数模板
        :param args_function 参数函数名称
        """
        self.unit_name = unit_name
        if plugin_name is None:
            self.plugin_name = unit_name
        else:
            self.plugin_name = plugin_name
        self.auto_imports = auto_imports
        self.args_template = args_template
        self.args_function = args_function

    @property
    def unit_type(self):
        return "plugin_job"

    def gen_code(self):
        if self.args_template:
            return """
        Job(
            name="{unit_name}",
            plugin_name="{plugin_name}",
            args={args}
        ),\n""".format(
                unit_name=self.unit_name,
                plugin_name=self.plugin_name,
                args=self.args_template
            )
        elif self.args_function:
            return """
        Job(
            name="{unit_name}",
            plugin_name="{plugin_name}",
            args={args}
        ),\n""".format(
                unit_name=self.unit_name,
                plugin_name=self.plugin_name,
                args=self.args_function
            )
        else:
            return """
        Job(
            name="{unit_name}",
            plugin_name="{plugin_name}"
        ),\n""".format(unit_name=self.unit_name, plugin_name=self.plugin_name)


class CallerBasedJobTemplate(CodeTemplate):

    """基于函数的Job模板
    """

    def __init__(self, unit_name, caller=None):
        """
        :param unit_name Job名称
        :param caller 函数名称，如果为None则为lambda表达式
        """
        self.unit_name = unit_name
        self.caller = caller

    @property
    def unit_type(self):
        return "caller_job"

    def gen_code(self):
        if self.caller is None:
            return """
        Job(
            name="{unit_name}",
            caller=lambda ctx: None,
        ),\n""".format(
                unit_name=self.unit_name,
            )
        else:
            return """
        Job(
            name="{unit_name}",
            caller={caller},
        ),\n""".format(unit_name=self.unit_name, caller=self.caller)


class DecisionTemplate(CodeTemplate):

    """Decision Code Template
    """

    def __init__(self, unit_name, decision_function=None):
        self.unit_name = unit_name
        self.decision_function = decision_function

    @property
    def unit_type(self):
        return "decision"

    def gen_code(self):
        if self.decision_function:
            return """
        Decision(
            {unit_name},
            {decision_function}
        ),\n""".format(
                unit_name=self.unit_name,
                decision_function=self.decision_function
            )
        else:
            return """
        Decison(
            {unit_name},
            lambda ctx: None
        ),\n""".format(unit_name=self.unit_name)

plugin_args_templates = {
    "read_csv": """(
                CSVR(),
            )""",
}


plugin_auto_imports = {
    "read_csv": [
        "from girlfriend.plugin.csv import CSVR"
    ]
}


class WorkflowGenerator(cmd.Cmd):

    def __init__(self, file_name):
        cmd.Cmd.__init__(self)
        self.units = []
        self.file_name = file_name

    def do_plugin_job(self, line):
        """
        :param line 格式：工作单元名称 [插件名称] [参数函数名]
        """
        cmd_args = line.split(" ")
        unit_name = cmd_args[0].strip()

        if unit_name in self.units:
            print colored(u"工作单元 '{}' 已经存在".format(unit_name), "red")
            return

        if len(cmd_args) >= 2:
            plugin_name = cmd_args[1].strip()
        else:
            plugin_name = None
        if len(cmd_args) >= 3:
            arg_function = cmd_args[2].strip()
        else:
            arg_function = None

        args = plugin_args_templates.get("read_csv", None)
        auto_imports = plugin_auto_imports.get("read_csv", None)
        if arg_function:
            job_tpl = PluginBasedJobTemplate(
                unit_name, plugin_name, auto_imports, None, arg_function)
        else:
            job_tpl = PluginBasedJobTemplate(
                unit_name, plugin_name, auto_imports, args)
        self.units.append(job_tpl)

    def do_plugin(self, line):
        return self.do_plugin_job(line)

    def do_caller_job(self, line):
        """
        :param line 格式：工作单元名称 [执行函数名]
        """
        cmd_args = line.split(" ")
        unit_name = cmd_args[0].strip()

        if unit_name in self.units:
            print colored(u"工作单元 '{}' 已经存在".format(unit_name), "red")
            return

        if len(cmd_args) >= 2:
            func_name = cmd_args[1].strip()
        else:
            func_name = None

        job_tpl = CallerBasedJobTemplate(unit_name, func_name)
        self.units.append(job_tpl)

    def do_caller(self, line):
        return self.do_caller_job(line)

    def do_decision(self, line):
        cmd_args = line.split(" ")
        unit_name = cmd_args[0].strip()
        if len(cmd_args) >= 1:
            decision_function = cmd_args[1].strip()
        else:
            decision_function = None
        decision_unit = DecisionTemplate(unit_name, decision_function)
        self.units.append(decision_unit)

    def do_remove(self, line):
        if line not in self.units:
            print colored(u"找不到工作单元 '{}'".format(line), "red")
            return
        return self.units.remove(line)

    def _generate_workflow_code(self):
        # 记录已经导入的项目
        imported = set()
        generated_functions = set()

        # coding
        yield "# coding: utf-8\n"
        yield "\n"

        # docs
        yield "\"\"\"\n"
        yield "Docs goes here\n"
        yield "\"\"\"\n"
        yield "\n"

        # import
        yield "import argparse\n"
        yield "from girlfriend.workflow.gfworkflow import Job, Decision\n"
        for unit in self.units:
            if unit.unit_type != "plugin_job":
                continue
            for import_item in unit.auto_imports:
                if import_item in imported:
                    continue
                imported.add(import_item)
                yield import_item + "\n"
        yield "\n"
        yield "\n"

        # workflow
        yield "def workflow(options):\n"
        yield "    work_units = (\n"
        for unit in self.units:
            yield "        # {}".format(unit.unit_name)
            yield unit.gen_code()
        yield "\n"
        yield "    )\n"
        yield "\n"
        yield "    return work_units\n"
        yield "\n"
        yield "\n"

        # args function
        for unit in self.units:

            args_function = None
            if unit.unit_type == "plugin_job":
                args_function = getattr(unit, "args_function", None)
            elif unit.unit_type == "caller_job":
                args_function = getattr(unit, "caller", None)
            elif unit.unit_type == "decision":
                args_function = getattr(unit, "decision_function", None)

            if args_function is not None:
                if args_function in generated_functions:
                    continue
                generated_functions.add(args_function)
                yield "def {function_name}(context):\n".format(
                    function_name=args_function)
                yield "    pass\n"
                yield "\n"

    def do_show(self, line):
        code = "".join(self._generate_workflow_code())
        print colored(code, "green")

    def do_gen(self, line):
        answer = raw_input(u"确定要生成代码？(y/n)".encode("utf-8"))
        if answer == "y":
            with open(self.file_name, "w") as f:
                f.write("".join(self._generate_workflow_code()))
        return True

    def do_EOF(self, line):
        return self.do_gen(line)


def gen(path, options):
    WorkflowGenerator(options.file_name).cmdloop()
