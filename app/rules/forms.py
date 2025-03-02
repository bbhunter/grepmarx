# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021 - present Orange Cyberdefense
"""

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectMultipleField, widgets
from wtforms.fields.simple import HiddenField, StringField
from wtforms.validators import DataRequired, Regexp


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RulePackForm(FlaskForm):
    id = HiddenField("Rule pack id", id="rule-pack-id")
    name = StringField("Rule pack name", id="rule-pack-name", validators=[DataRequired()])
    description = TextAreaField("Rule pack description", id="rule-pack-description")
    languages = MultiCheckboxField("Languages", coerce=int, validators=[DataRequired()])
    rules = HiddenField("Rule pack rules", id="datatable-selection")

class RulesAddForm(FlaskForm):
    name = StringField("Name of rule", id="rule-name", validators=[DataRequired(),Regexp(
                "^[a-zA-Z0-9-_ ]+$",
                message="Rule name must contain only letters, numbers, dash (-), underscore (_) or space ( ) characters",
            ),])
    rule = TextAreaField("Rule code", id="rule-code", validators=[DataRequired()])
