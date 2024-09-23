from flask_wtf import FlaskForm
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms import (
    SubmitField,
    SelectMultipleField,
)


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class AccessForm(FlaskForm):
    submit = SubmitField("Access")