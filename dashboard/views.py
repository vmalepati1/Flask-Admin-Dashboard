from dashboard import app, db, login_manager, images
from flask import Flask, url_for, redirect, render_template, request
import flask_login as login
from dashboard.models import *
from dashboard.forms import *
from dashboard.config import UPLOADED_IMAGES_DEST, UPLOADED_IMAGES_URL
from flask_admin import Admin, AdminIndexView, expose, helpers, form
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.view import func
from sqlalchemy import event
from sqlalchemy.event import listen
from werkzeug.utils import secure_filename
import os.path as op
from dashboard.utils import *

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
        'img_url': form.ImageUploadField(base_path=UPLOADED_IMAGES_DEST, url_relative_path='img/', namegen=imagename_uuid1_gen)
    }
    column_formatters = {
        'icon': list_thumbnail,
        'img_url': lambda v, c, m, p: images.url(m.img_url) if m.img_url else None
    }

    def on_model_change(self, form, model, is_created):
        manage_updates(model, is_created)
    
    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.IS_admin

class CategoryToCompanyAssignmentView(ModelView):

    form_columns = ('Company_ID', 'Category_ID')
    column_labels = {'parent_com.Company_Name': 'Company Name',
                     'parent_cat.Category_Name': 'Category Name'}
    column_searchable_list = ['Category_ID', 'parent_com.Company_Name', 'parent_cat.Category_Name']
    column_list = ['id', 'Company_ID'] + column_searchable_list

    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.IS_admin

class CompanyView(ModelView):

    column_display_pk = True
    column_labels = {'img_url': 'Logo URL'}
    form_columns = ['Company_ID', 'Company_Name', 'Address1', 'Address2', 'City', 'State',
                   'Country', 'Phone1', 'Cell_note', 'img_url']
    column_list = form_columns + ['logo']
    form_extra_fields = {
        'img_url': form.ImageUploadField(base_path=UPLOADED_IMAGES_DEST, url_relative_path='img/', namegen=imagename_uuid1_gen)
    }
    column_formatters = {
        'logo': list_thumbnail,
        'img_url': lambda v, c, m, p: images.url(m.img_url) if m.img_url else None
    }
    column_searchable_list = ['Company_Name']

    @property
    def can_create(self):
        return login.current_user.IS_admin

    @property
    def can_delete(self):
        return login.current_user.IS_admin
    
    def get_query(self):
        if login.current_user.IS_admin:
            return self.session.query(self.model)
        
        return self.session.query(self.model).filter(self.model.Company_ID==login.current_user.Company_ID)

    def get_count_query(self):
        if login.current_user.IS_admin:
            return self.session.query(func.count('*'))
        
        return self.session.query(func.count('*')).filter(self.model.Company_ID==login.current_user.Company_ID)

    def is_accessible(self):
        return login.current_user.is_authenticated

class CompanyDeliveryView(ModelView):

    column_searchable_list = ['parent_com.Company_Name', 'delivery_name', 'delivery_desc', 'delivery_cost']
    column_labels = {'parent_com.Company_Name': 'Company Name'}
    form_columns = ['Company_ID', 'delivery_name', 'delivery_desc', 'delivery_cost']
    column_list = ['delivery_id', 'Company_ID'] + column_searchable_list
    
    @property
    def can_create(self):
        return login.current_user.IS_admin

    @property
    def can_delete(self):
        return login.current_user.IS_admin
    
    def get_query(self):
        if login.current_user.IS_admin:
            return self.session.query(self.model)
        
        return self.session.query(self.model).filter(self.model.Company_ID==login.current_user.Company_ID)

    def get_count_query(self):
        if login.current_user.IS_admin:
            return self.session.query(func.count('*'))
        
        return self.session.query(func.count('*')).filter(self.model.Company_ID==login.current_user.Company_ID)

    def is_accessible(self):
        return login.current_user.is_authenticated

class CompanyTimetableView(ModelView):

    column_searchable_list = ['parent_com.Company_Name']
    column_labels = {'parent_com.Company_Name': 'Company Name'}
    form_columns = ['Company_ID', 'weekday', 'open_time', 'close_time']
    column_list = ['timetable_id', 'Company_ID', 'parent_com.Company_Name'] + form_columns[1:]
    
    @property
    def can_create(self):
        return login.current_user.IS_admin

    @property
    def can_delete(self):
        return login.current_user.IS_admin
    
    def get_query(self):
        if login.current_user.IS_admin:
            return self.session.query(self.model)
        
        return self.session.query(self.model).filter(self.model.Company_ID==login.current_user.Company_ID)

    def get_count_query(self):
        if login.current_user.IS_admin:
            return self.session.query(func.count('*'))
        
        return self.session.query(func.count('*')).filter(self.model.Company_ID==login.current_user.Company_ID)

    def is_accessible(self):
        return login.current_user.is_authenticated

class OperatorView(ModelView):
    column_searchable_list = ['Operator_ID', 'First_name', 'Last_name', 'Mobile_num',
                              'Email', 'Username', 'parent_com.Company_Name']
    column_labels = {'parent_com.Company_Name': 'Company Name'}
    form_columns = ['First_name', 'Last_name', 'Mobile_num', 'Mobile_confirmed',
                    'Email', 'Username', 'Password', 'Company_ID']
    column_list = ['Operator_ID'] + form_columns[:5] + ['Created_at', 'Modified_at'] + \
                  form_columns[6:] + ['parent_com.Company_Name', 'IS_admin']
    
    @property
    def can_create(self):
        return login.current_user.IS_admin

    @property
    def can_delete(self):
        return login.current_user.IS_admin

    def get_query(self):
        if login.current_user.IS_admin:
            return self.session.query(self.model)
        
        return self.session.query(self.model).filter(self.model.Operator_ID==login.current_user.Operator_ID)

    def get_count_query(self):
        if login.current_user.IS_admin:
            return self.session.query(func.count('*'))
        
        return self.session.query(func.count('*')).filter(self.model.Operator_ID==login.current_user.Operator_ID)

    def on_model_change(self, form, model, is_created):
        manage_updates(model, is_created)
    
    def is_accessible(self):
        return login.current_user.is_authenticated

class CartView(ModelView):
    column_searchable_list = ['User_ID', 'parent_user.First_name', 'parent_user.Last_name',
                              'parent_user.Mobile_num', 'parent_user.Email', 'parent_user.Username']
    form_columns = ['User_ID', 'Operator_ID', 'DatePlaced', 'HomeDelivery',
                    'DateDelivery', 'Confirmed', 'Delivered', 'cart_note']
    column_list = ['id', 'User_ID', 'parent_user.Username', 'Operator_ID', 'parent_op.Username'] + \
                  form_columns[2:7] + ['Created_at', 'Modified_at', 'cart_note']
    column_labels = {'parent_user.Username': 'User Username',
                     'parent_op.Username': 'Operator Username',
                     'DatePlaced': 'Date Placed',
                     'HomeDelivery': 'Home Delivery',
                     'DateDelivery': 'Date Delivery'}
    
    def on_model_change(self, form, model, is_created):
        manage_updates(model, is_created)
    
    def is_accessible(self):
        return login.current_user.is_authenticated

class ProductView(ModelView):
    form_columns = ['productName', 'productDescription', 'productCost', 'productWeight', 'img_url',
                    'productInStock']
    column_list = ['id'] + form_columns[:5] + ['image', 'productInStock', 'Created_at', 'Modified_at']
    column_labels = {'productName': 'Product Name',
                     'productDescription': 'Product Description',
                     'productCost': 'Product Cost',
                     'productWeight': 'Product Weight',
                     'img_url': 'Product Image URL',
                     'productInStock': 'Product In Stock'}
    form_extra_fields = {
        'img_url': form.ImageUploadField(base_path=UPLOADED_IMAGES_DEST, url_relative_path='img/', namegen=imagename_uuid1_gen)
    }
    column_formatters = {
        'image': list_thumbnail,
        'img_url': lambda v, c, m, p: images.url(m.img_url) if m.img_url else None
    }    

    def on_model_change(self, form, model, is_created):
        manage_updates(model, is_created)

    def is_accessible(self):
        return login.current_user.is_authenticated

class CartDetailView(ModelView):
    column_searchable_list = ['Cart_ID', 'parent_com.categories.Category_Name', 'parent_prod.productName']
    form_columns = ['Cart_ID', 'Prodcut_ID', 'Company_ID', 'Quantity', 'DatePlaced']
    column_list = ['id', 'Cart_ID', 'Prodcut_ID', 'parent_prod.productName', 'Company_ID', 'parent_com.Company_Name', 'Quantity', 'DatePlaced']
    column_labels = {'parent_prod.productName': 'Product Name',
                     'parent_com.Company_Name': 'Company Name',
                     'DatePlaced': 'Date Placed'}
    
    def is_accessible(self):
        return login.current_user.is_authenticated

class ProductGalleryView(ModelView):
    column_searchable_list = ['product_id', 'parent_prod.productName']
    form_columns = ['product_id', 'img_url']
    column_list = ['id', 'product_id', 'parent_prod.productName', 'img_url', 'product_image']
    column_labels = {
        'parent_prod.productName': 'Product Name',
        'img_url': 'Product Image URL' 
    }
    form_extra_fields = {
        'img_url': form.ImageUploadField(base_path=UPLOADED_IMAGES_DEST, url_relative_path='img/', namegen=imagename_uuid1_gen)
    }
    column_formatters = {
        'product_image': list_thumbnail,
        'img_url': lambda v, c, m, p: images.url(m.img_url) if m.img_url else None
    }
    
    def is_accessible(self):
        return login.current_user.is_authenticated

class ServicesCatView(ModelView):
    column_searchable_list = ['Servicecat_ID', 'parent_com.Company_Name', 'Category_Name']
    form_columns = ['Company_ID', 'Category_Name', 'Parent_Category_ID', 'img_url']
    column_list = ['Servicecat_ID', 'Company_ID', 'parent_com.Company_Name', 'Category_Name',
                   'Parent_Category_ID', 'img_url', 'icon', 'Created_at', 'Modified_at']
    column_labels = {
        'parent_com.Company_Name': 'Company Name',
        'img_url': 'Icon URL' 
    }
    form_extra_fields = {
        'img_url': form.ImageUploadField(base_path=UPLOADED_IMAGES_DEST, url_relative_path='img/', namegen=imagename_uuid1_gen)
    }
    column_formatters = {
        'icon': list_thumbnail,
        'img_url': lambda v, c, m, p: images.url(m.img_url) if m.img_url else None
    }

    def on_model_change(self, form, model, is_created):
        manage_updates(model, is_created)
    
    def is_accessible(self):
        return login.current_user.is_authenticated and login.current_user.IS_admin

class ServiceSlotView(ModelView):
    column_searchable_list = ['Slot_ID', 'Service_ID', 'Reservation_ID']
    column_display_pk = True
    
    def is_accessible(self):
        return login.current_user.is_authenticated

class UserView(ModelView):

    column_searchable_list = ['User_ID', 'First_name', 'Last_name', 'Address1', 'Address2',
                              'Mobile_num', 'Email', 'Username', 'invoice_name', 'invoice_address']
    a = [m.key for m in User().__table__.columns]
    all_attrs = ['img_url' if c == 'Photo_url' else c for c in a]
    form_columns = all_attrs[1:]
    column_list = all_attrs[:20] + ['photo'] + all_attrs[20:]
    column_labels = {
        'img_url': 'Photo URL' 
    }
    form_extra_fields = {
        'img_url': form.ImageUploadField(base_path=UPLOADED_IMAGES_DEST, url_relative_path='img/', namegen=imagename_uuid1_gen)
    }
    column_formatters = {
        'photo': list_thumbnail,
        'img_url': lambda v, c, m, p: images.url(m.img_url) if m.img_url else None
    }
    
    @property
    def can_edit(self):
        return login.current_user.is_authenticated

    @property
    def can_delete(self):
        return login.current_user.is_authenticated
    
    def get_query(self):
        if login.current_user.is_authenticated:
            return self.session.query(self.model)
        
        return self.session.query(self.model).filter(False)

    def get_count_query(self):
        if login.current_user.is_authenticated:
            return self.session.query(func.count('*'))
        
        return 0

    def on_model_change(self, form, model, is_created):
        manage_updates(model, is_created)

    def is_accessible(self):
        return True

# Delete callbacks
listen(Category, 'after_delete', delete_img)
listen(Company, 'after_delete', delete_img)
listen(Product, 'after_delete', delete_img)
listen(ProductGallery, 'after_delete', delete_img)
listen(ServicesCat, 'after_delete', delete_img)
listen(User, 'after_delete', delete_img)

admin = Admin(app, 'Dashboard', index_view=HomeLoginView(), base_template='master.html')
admin.add_view(CategoriesView(Category, db.session, category="Category"))
admin.add_view(CategoryToCompanyAssignmentView(CategoryCompanyAssignment, db.session, category="Category", name='Category <-> Company'))
admin.add_view(CompanyView(Company, db.session, category="Company"))
admin.add_view(CompanyDeliveryView(CompanyDelivery, db.session, category="Company"))
admin.add_view(CompanyTimetableView(CompanyTimetable, db.session, category="Company"))
admin.add_view(OperatorView(Operator, db.session, category="Company"))
admin.add_view(CartView(Cart, db.session, category="Cart"))
admin.add_view(CartDetailView(CartDetail, db.session, category="Cart"))
admin.add_view(ProductView(Product, db.session, category="Product"))
admin.add_view(ProductGalleryView(ProductGallery, db.session, category="Product"))
admin.add_view(ServicesCatView(ServicesCat, db.session, category="Services"))
admin.add_view(ServiceSlotView(ServiceSlot, db.session, category="Services"))
admin.add_view(UserView(User, db.session, name='User Registration'))
