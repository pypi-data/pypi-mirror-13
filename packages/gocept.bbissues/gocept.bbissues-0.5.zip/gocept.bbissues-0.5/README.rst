================================
The gocept.bbissues distribution
================================

Collect open issues from multiple bitbucket repositories and generate a nice html page.

This package is compatible with Python version 2.7.

Installation
============

Install the package using PIP::

    $ pip install gocept.bbissues


Configuration
=============

You have to provide a config file with the following content::

    [config]
    log = issues.log
    # The next line is optional it defaults to index.jj2 in the package
    template_path = template.jj2

    [bitbucket]
    projects = owner:project1
               owner:project2

    [github]
    projects = owner:project1
               owner:project2


The template will be rendered using jinja2, and could have the following content::

    {% for project in projects %}
        <h2>{{project.name}}</h2>
        {% for issue in project.issues %}
            <h3>{{issue.title}}</h3>
             <pre>
             {{issue.title}}
             {{issue.content}}
             {{issue.status}}
             {{issue.created}}
             {{issue.priority}}
             {{issue.url}}
             {{issue.author}}
             </pre>
        {% endfor %}
    {% endfor %}


Usage
=====

Call it using::

    $ <path to bin directory>/bbissues --config <path to config file>

It prints the generated HTML to the console. You might need to redirect the
output to a file.

