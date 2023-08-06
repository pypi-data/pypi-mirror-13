#!/usr/bin/env python

# Script Name		: creator.py
# Author			: Tony Hammack
# Created			: 23 February 2016
# Last Modified		: 23 February 2016
# Version			: 1.0

# ***** Classes Imported
from datetime import datetime

from jinja2 import Environment, FileSystemLoader


# ***** Functions *****

def script_name():
    # Creates script name
    script = raw_input("What is the name of the script? : ")
    script = (script + '.py')
    return script


def author_name():
    # Creates author of script
    author = raw_input("What is the author of the script? : ")
    return author


def date_created():
    # Creates Date
    current_date = datetime.now()
    c_date = str(current_date)
    c_date = c_date[:10]
    return c_date


def build_template():
    # Returns variables
    scriptName = script_name()
    author = author_name()
    date = date_created()

    # Loads default template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("template.py")

    # Dictionary for template engine
    template_vars = {
            "scriptName" : scriptName,
            "author": author,
            "date": date
                     }
    # Returns output
    output = template.render(template_vars)

    # Function for writing output to file
    def createPython(output):
        f = open(scriptName, 'w')
        f.write(output)
        f.close()

    createPython(output)

# **** Start of Program
if __name__ == "__main__":
    # Builds Template
    build_template()




