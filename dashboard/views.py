from dashboard import app, db, login_manager, images
from flask import Flask, url_for, redirect, render_template, request
import flask_login as login
from dashboard.models import *
from dashboard.forms import *
from dashboard.config import UPLOADED_IMAGES_DEST, UPLOADED_IMAGES_URL
from flask_admin import Admin, AdminIndexView, expose, helpers, form
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import event
from sqlalchemy.event import listen
from werkzeug.utils import secure_filename
import os.path as op
from dashboard.utils import delete_img, _list_thumbnail, _imagename_uuid1_gen

# Directs user to admin
@app.route('/')
def index():
    return render_template('index.html')

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
                    'Parent_Category_ID', 'img_url')
    column_labels = {'img_url': 'Icon URL'}
    column_list = form_columns + ('icon', 'Created_at', 'Modified_at')
    form_extra_fields = {
        'img_url': form.ImageUploadField(base_path=UPLOADED_IMAGES_DEST, url_relative_path='img/')
    }
    column_formatters = {
        'icon': _list_thumbnail,
        'img_url': lambda v, c, m, p: images.url(m.img_url) if m.img_url else None
    }
    
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

# Delete callbacks
listen(Category, 'after_delete', delete_img)

admin = Admin(app, 'Dashboard', index_view=HomeLoginView(), base_template='master.html')
admin.add_view(CategoriesView(Category, db.session, category="Category"))
admin.add_view(CategoryToCompanyAssignmentView(CategoryCompanyAssignment, db.session, category="Category", name='Category <-> Company'))
admin.add_view(CompanyView(Company, db.session, category="Company"))
