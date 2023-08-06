#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A tool can programmatically generate Html Text snippet for single page
application html templates.

ref: http://www.w3schools.com/tags/tag_input.asp


Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Python2: Yes
- Python3: Yes


Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- None


Class, method, function, exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from __future__ import print_function, unicode_literals

class HtmlConstructor(object):
    tab = "    "
    
    def input_text(self, name, size=30):
        """
        """
        return '<input type="text" name="%s" size="%s" value="{{%s}}" />' % (name, size, name)
        
    def input_number(self, name, size=30):
        return '<input type="number" name="%s" size="%s" value="{{%s}}" />' % (name, size, name)
    
    def input_float(self, name, precision=2, size=30):
        if precision == 0:
            step = 1
        else:
            step = "0.%s1" % ("0" * (precision - 1))
        return '<input type="number" step="%s" name="%s" size="%s" value="{{%s}}" />' % (step, name, size, name)
    
    def input_date(self, name, size=30):
        return '<input type="date" name="%s" size="%s" value="{{%s}}" />' % (name, size, name)
    
    def input_time(self, name, size=30):
        return '<input type="time" name="%s" size="%s" value="{{%s}}" />' % (name, size, name)

    def input_ratio(self, name, choices, labels, multi_line=False):
        """        
        {% for value, label in [('choice1', '选项1'), ('choice2', '选项2')] %}
            {% if ratio == value %}
                {% set checked = "checked" %}
            {% else %}
                {% set checked = "" %}
            {% endif %}
            <input type="radio" name="ratio" value="{{value}}" {{checked}} /> {{label}}
        {% endfor %}
        """
        if len(choices) != len(labels):
            raise ValueError("The size of 'choices' and 'labels' doesn't match!")
        
        choice_label = list(zip(choices, labels))
        
        lines = list()
        lines.append('{%% for value, label in %s %%}' % repr(choice_label))
        lines.append(self.tab + '{%% if %s == value %%}' % name)
        lines.append(self.tab * 2 + '{% set checked = "checked" %}')
        lines.append(self.tab + '{% else %}')
        lines.append(self.tab * 2 + '{% set checked = "" %}')
        lines.append(self.tab + '{% endif %}')
        if multi_line:
            line_break = "<br>"
        else:
            line_break = ""
        lines.append(self.tab + '<input type="radio" name="%s" value="{{value}}" {{checked}} /> {{label}} %s' % (name, line_break))
        lines.append('{% endfor %}')
        return "\n".join(lines)
    
    def input_check(self, name, label, multi_line=False):
        """
        {% if multiple_choice_1 %}
            {% set checked = "checked" %}
        {% else %}
            {% set checked = "" %}
        {% endif %}
        <input type="checkbox" name="multiple_choice_1" value="multiple_choice_1" {{checked}}> multiple_choice_1
        """
        lines = list()
        lines.append('{%% if %s %%}' % name)
        lines.append(self.tab + '{% set checked = "checked" %}')
        lines.append('{% else %}')
        lines.append(self.tab  + '{% set checked = "" %}')
        lines.append('{% endif %}')
        if multi_line:
            line_break = "<br>"
        else:
            line_break = ""
        lines.append('<input type="checkbox" name="%s" value="%s" {{checked}}> %s %s' % (name, name, label, line_break))        
        return "\n".join(lines)
    
    def input_textarea(self, name, form_id, rows=4, cols=50):
        return '<textarea name="%s" rows="%s" cols="%s" form="%s">{{%s}}</textarea>' % (
            name, rows, cols, form_id, name)
    
html_constructor = HtmlConstructor()


#--- Unittest ---
if __name__ == "__main__":
    print(html_constructor.input_text("text"))
    print(html_constructor.input_number("number"))
    print(html_constructor.input_float("float"))
    print(html_constructor.input_date("date"))
    print(html_constructor.input_date("time"))
    print(html_constructor.input_ratio(
        "ratio", ["choice1", "choice2"], ["选项1", "选项2"], multi_line=True))
    print(html_constructor.input_check("check", "是否选项"))
    print(html_constructor.input_textarea("textarea", "form_id"))
