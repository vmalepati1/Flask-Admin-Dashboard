from dashboard import db
from dashboard.models import Operator
from wtforms import form, fields, validators
import bcrypt

class LoginForm(form.Form):
    login = fields.StringField(u'Username/email', validators=[validators.required()])
    password = fields.PasswordField(u'Password', validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid username/email')

    def validate_password(self, field):
        user = self.get_user()

        if user is not None:
            db_hash = user.Password.encode()

            if not bcrypt.checkpw(self.password.data.encode(), db_hash):
                raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(Operator).filter(
            (Operator.Username==self.login.data) | (Operator.Email==self.login.data)).first()
