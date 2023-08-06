#! /usr/bin/env python
# coding: utf-8

import setuptools

install_requires = [
    "SQLAlchemy >= 1.0.0",
    "prettytable",
    "httpretty",
    "ujson",
    "termcolor >= 1.1.0",
    "requests >= 2.7.0",
    "fixtures >= 1.4.0"
]

setuptools.setup(
    name="girlfriend",
    version="0.0.2",
    author="Sam Chi",
    author_email="chihongze@gmail.com",
    description=(
        "A pure Python girlfriend "
        "she can help you build operation scripts, "
        "send data report, monitor the system "
        "and do a lot of things you undreamed!"
        "The most important, "
        "her heart(core lib) is all completely free!"
    ),
    license="MIT",
    packages=setuptools.find_packages("."),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "gf_workflow = girlfriend.tools.gf_workflow:main",
            "gf_config = girlfriend.tools.gf_config:main",
            "gf_gen = girlfriend.tools.gf_gen:main"
        ],

        # builtin plugins
        "girlfriend.plugin": [
            # db plugin
            "orm_query = girlfriend.plugin.orm:OrmQueryPlugin",

            # table plugin
            "table_adapter = girlfriend.plugin.table:TableAdapterPlugin",
            "column2title = girlfriend.plugin.table:TableColumn2TitlePlugin",
            "pretty_table = girlfriend.plugin.table:PrettyTablePlugin",
            "concat_table = girlfriend.plugin.table:ConcatTablePlugin",
            "join_table = girlfriend.plugin.table:JoinTablePlugin",

            # json plugin
            "json_reader = girlfriend.plugin.json:JsonReaderPlugin",
            "json_writer = girlfriend.plugin.json:JsonWriterPlugin",
        ]
    },
)
