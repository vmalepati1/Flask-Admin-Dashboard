from dashboard import app, db
from flask import Flask, url_for, redirect, render_template, request
import flask_login as login
from dashboard.models import *
from dashboard.forms import *
from flask_admin import Admin, AdminIndexView, expose, helpers
from flask_admin.contrib.sqla import ModelView

# Directs user to admin
@app.route('/')
def index():
    return render_template('index.html')

login_manager = login.LoginManager()
login_manager.init_app(app)

# Create user loader function
@login_manager.user_loader
def load_user(operator_id):
    return db.session.query(Operator).get(operator_id)

class HomeLoginView(AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(HomeLoginView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        
        self._template_args['form'] = form
        
        return super(HomeLoginView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

class CategoriesView(ModelView):
    
    form_columns = ('Category_ID', 'Category_Name',
                    'Parent_Category_ID', 'ICON_URL')
    column_list = form_columns + ('Created_at', 'Modified_at')

    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.IS_admin

class CategoryToCompanyAssignmentView(ModelView):

    form_columns = ('Company_ID', 'Category_ID')
    column_list = tuple(form_columns)

    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.IS_admin

class CompanyView(ModelView):

    column_display_pk = True
    form_excluded_columns = ('children')

    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.IS_admin
    
admin = Admin(app, 'Dashboard', index_view=HomeLoginView(), base_template='master.html')
admin.add_view(CategoriesView(Category, db.session))
admin.add_view(CategoryToCompanyAssignmentView(CategoryCompanyAssignment, db.session))
admin.add_view(CompanyView(Company, db.session))
