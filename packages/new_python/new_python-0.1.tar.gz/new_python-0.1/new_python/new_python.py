from datetime import datetime
from jinja2 import Environment, FileSystemLoader





def script_name():
    script = raw_input("What is the name of the script? : ")
    script = (script + '.py')
    return script


def author_name():
    author = raw_input("What is the author of the script? : ")
    return author


def date_created():
    current_date = datetime.now()
    c_date = str(current_date)
    c_date = c_date[:10]
    return c_date


def build_template():
    scriptName = script_name()
    author = author_name()
    date = date_created()


    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("template.py")

    template_vars = {"scriptName" : scriptName,
                 "author": author,
                 "date": date}

    output = template.render(template_vars)

    def createPython(output):
        f = open(scriptName, 'w')
        f.write(output)
        f.close()

    createPython(output)



build_template()




