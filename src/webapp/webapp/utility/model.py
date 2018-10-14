from wtforms import Form, StringField, validators

class input_form(Form):
    # floating point var inputedv - default validator checks for real number
    # input req validator requires value
    # r = StringField(validators=[validatoxrs.InputRequired()])
    r = '9'#TODO change
