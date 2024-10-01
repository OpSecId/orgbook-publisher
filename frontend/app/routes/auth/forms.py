from flask_wtf import FlaskForm
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms import (
    StringField,
    SubmitField,
    SelectMultipleField,
)


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class IssuerAccessForm(FlaskForm):
    submit = SubmitField("Access")

class AdminAccessForm(FlaskForm):
    admin_id = StringField('Admin Id')
    admin_key = StringField('Admin Key')
    submit = SubmitField("Access")
