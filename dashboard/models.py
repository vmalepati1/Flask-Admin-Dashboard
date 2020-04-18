from dashboard import db
from sqlalchemy.orm import backref

class Category(db.Model):
    __tablename__ = 'categories'

    Category_ID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    Category_Name = db.Column(db.String(500))
    Parent_Category_ID = db.Column(db.Integer, db.ForeignKey('categories.Category_ID'))
    img_url = db.Column('ICON_URL', db.String(500))
    Created_at = db.Column(db.TIMESTAMP)
    Modified_at = db.Column(db.TIMESTAMP)
    # Add cascade relationship for referential integrity
    children_int = db.relationship("Category", cascade="all, delete-orphan",
                backref=backref("parent", remote_side=[Category_ID])
            )

    children_assoc = db.relationship("CategoryCompanyAssignment", back_populates="parent_cat", cascade="all, delete-orphan")
    
    def __repr__(self):
        return '<Category %r>' % self.Category_Name

class Company(db.Model):
    Company_ID = db.Column(db.Integer, primary_key=True)
    Company_Name = db.Column(db.String(500))
    Address1 = db.Column(db.String(500))
    Address2 = db.Column(db.String(500))
    City = db.Column(db.String(45))
    State = db.Column(db.String(45))
    Country = db.Column(db.String(45))
    Phone1 = db.Column(db.String(100))
    Cell_note = db.Column(db.String(100))
    img_url = db.Column('Logo_URL', db.String(500))

    categories = db.relationship('Category', secondary='category_company_assignment')
    children_assoc = db.relationship("CategoryCompanyAssignment", back_populates="parent_com", cascade="all, delete-orphan")
    children_deliv = db.relationship("CompanyDelivery", back_populates="parent_com", cascade="all, delete-orphan")
    children_time = db.relationship("CompanyTimetable", back_populates="parent_com", cascade="all, delete-orphan")
    children_op = db.relationship("Operator", back_populates="parent_com", cascade="all, delete-orphan")
    children_cart_det = db.relationship("CartDetail", back_populates="parent_com", cascade="all, delete-orphan")
    children_scat = db.relationship("ServicesCat", back_populates="parent_com", cascade="all, delete-orphan")
    
    def __repr__(self):
        return '<Company %r>' % self.Company_Name

# Association table of company to categories - many to many - 
class CategoryCompanyAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Company_ID = db.Column(db.Integer, db.ForeignKey('company.Company_ID'), primary_key=True)
    Category_ID = db.Column(db.Integer, db.ForeignKey('categories.Category_ID'), primary_key=True)
    parent_com = db.relationship("Company", back_populates="children_assoc")
    parent_cat = db.relationship("Category", back_populates="children_assoc")

    def __repr__(self):
        return '<Category <-> Company %r>' % self.id

class CompanyDelivery(db.Model):
    delivery_id = db.Column(db.Integer, primary_key=True)
    Company_ID = db.Column(db.Integer, db.ForeignKey('company.Company_ID'))
    delivery_name = db.Column(db.String(100))
    delivery_desc = db.Column(db.String(500))
    delivery_cost = db.Column(db.DECIMAL(2))

    parent_com = db.relationship("Company", back_populates="children_deliv")

    def __repr__(self):
        return '<Company Delivery %r>' % self.delivery_name

class CompanyTimetable(db.Model):
    timetable_id = db.Column(db.Integer, primary_key=True)
    Company_ID = db.Column(db.Integer, db.ForeignKey('company.Company_ID'))
    weekday = db.Column(db.Integer)
    open_time = db.Column(db.TIME)
    close_time = db.Column(db.TIME)

    parent_com = db.relationship("Company", back_populates="children_time")

    def __repr__(self):
        return '<Company Timetable %r>' % self.timetable_id

class User(db.Model):
    User_ID		 = db.Column(db.Integer, primary_key=True)
    First_name		 = db.Column(db.String(100))
    Last_name		 = db.Column(db.String(100))
    Address1		 = db.Column(db.String(500))
    Address2		 = db.Column(db.String(500))
    Address_num		 = db.Column(db.String(15))
    Address_note	 = db.Column(db.String(500))
    zip_code		 = db.Column(db.String(15))
    City		 = db.Column(db.String(100))
    Province		 = db.Column(db.String(100))
    State		 = db.Column(db.String(100))
    Country		 = db.Column(db.String(100))
    Mobile_num		 = db.Column(db.String(100))
    Mobile_confirmed     = db.Column(db.Boolean)
    Email		 = db.Column(db.String(500))
    Created_at		 = db.Column(db.TIMESTAMP)
    Modified_at		 = db.Column(db.TIMESTAMP)
    Username		 = db.Column(db.String(100))
    Password		 = db.Column(db.String(255))
    img_url		 = db.Column('Photo_url', db.String(500))
    invoice_need	 = db.Column(db.Boolean)
    invoice_name	 = db.Column(db.String(250))
    invoice_cf		 = db.Column(db.String(20))
    invoice_piva	 = db.Column(db.String(20))
    invoice_address	 = db.Column(db.String(500))
    invoice_addrnum	 = db.Column(db.String(15))
    invoice_zip		 = db.Column(db.String(15))
    invoice_City	 = db.Column(db.String(100))
    invoice_Province     = db.Column(db.String(100))
    invoice_region	 = db.Column(db.String(100))
    invoice_country	 = db.Column(db.String(100))

    children_cart = db.relationship("Cart", back_populates="parent_user", cascade="all, delete-orphan")

    def __repr__(self):
        return '<User %r>' % self.Username

class Cart(db.Model):
    id		 = db.Column(db.Integer, primary_key=True)
    User_ID	 = db.Column(db.Integer, db.ForeignKey('user.User_ID'))
    Operator_ID	 = db.Column(db.Integer, db.ForeignKey('operators.Operator_ID'))
    DatePlaced	 = db.Column(db.DATETIME)
    HomeDelivery = db.Column(db.Boolean)
    DateDelivery = db.Column(db.DATETIME)
    Confirmed	 = db.Column(db.Boolean, default=False)
    Delivered	 = db.Column(db.Boolean, default=False)
    Created_at	 = db.Column(db.TIMESTAMP)
    Modified_at	 = db.Column(db.TIMESTAMP)
    cart_note	 = db.Column(db.String(500))

    parent_user = db.relationship("User", back_populates="children_cart")
    parent_op = db.relationship("Operator", back_populates="children_cart")

    children_cart_det = db.relationship("CartDetail", back_populates="parent_cart", cascade="all, delete-orphan")

    def __repr__(self):
        return '<Cart %r>' % self.id

class Product(db.Model):
    id			         = db.Column(db.Integer, primary_key=True)
    productName 		 = db.Column(db.String(255))
    productDescription	         = db.Column(db.String(1000))
    productCost			 = db.Column(db.DECIMAL(2))
    productWeight		 = db.Column(db.DECIMAL(2))
    img_url		         = db.Column('productImageUrl', db.String(500))
    productInStock		 = db.Column(db.Integer)
    Created_at			 = db.Column(db.TIMESTAMP)
    Modified_at			 = db.Column(db.TIMESTAMP)

    children_cart_det = db.relationship("CartDetail", back_populates="parent_prod", cascade="all, delete-orphan")
    children_pgal = db.relationship("ProductGallery", back_populates="parent_prod", cascade="all, delete-orphan")

    def __repr__(self):
        return '<Product %r>' % self.productName

class CartDetail(db.Model):
    id		= db.Column(db.Integer, primary_key=True)
    Cart_ID	= db.Column(db.Integer, db.ForeignKey('cart.id'))
    Prodcut_ID	= db.Column(db.Integer, db.ForeignKey('product.id'))
    Company_ID	= db.Column(db.Integer, db.ForeignKey('company.Company_ID'))
    Quantity	= db.Column(db.Integer)
    DatePlaced	= db.Column(db.DATETIME)

    parent_cart = db.relationship("Cart", back_populates="children_cart_det")
    parent_prod = db.relationship("Product", back_populates="children_cart_det")
    parent_com = db.relationship("Company", back_populates="children_cart_det")

    def __repr__(self):
        return '<Cart Detail %r>' % self.id

class ProductGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    img_url = db.Column('product_image', db.String(500))

    parent_prod = db.relationship("Product", back_populates="children_pgal")

class ServicesCat(db.Model):
    Servicecat_ID 	= db.Column(db.Integer, primary_key=True)
    Company_ID		= db.Column(db.Integer, db.ForeignKey('company.Company_ID'))
    Category_Name	= db.Column(db.String(500))
    Parent_Category_ID	= db.Column(db.Integer, db.ForeignKey('services_cat.Servicecat_ID'))
    img_url		= db.Column('ICON_URL', db.String(500))
    Created_at		= db.Column(db.TIMESTAMP)
    Modified_at		= db.Column(db.TIMESTAMP)

    children_int = db.relationship("ServicesCat", cascade="all, delete-orphan",
                backref=backref("parent", remote_side=[Servicecat_ID])
            )
    
    parent_com = db.relationship("Company", back_populates="children_scat")

class ServiceSlot(db.Model):
    Slot_ID	    	= db.Column(db.Integer, primary_key=True)
    Service_Slot_date	= db.Column(db.DATETIME)
    Slot_Start_time	= db.Column(db.TIME)
    Slot_end_time	= db.Column(db.TIME)
    Service_ID		= db.Column(db.Integer)
    Reservation_ID	= db.Column(db.Integer)
    Is_available	= db.Column(db.Boolean)

class Operator(db.Model):
    __tablename__ = 'operators'
    
    Operator_ID = db.Column(db.Integer, primary_key=True)
    First_name = db.Column(db.String(100))
    Last_name = db.Column(db.String(100))
    Mobile_num = db.Column(db.String(100))
    Mobile_confirmed = db.Column(db.Boolean)
    Email = db.Column(db.String(500))
    Created_at = db.Column(db.TIMESTAMP)
    Modified_at = db.Column(db.TIMESTAMP)
    Username = db.Column(db.String(100))
    Password = db.Column(db.String(255))
    Company_ID = db.Column(db.Integer, db.ForeignKey('company.Company_ID'))
    IS_admin = db.Column(db.Boolean)

    children_cart = db.relationship("Cart", back_populates="parent_op", cascade="all, delete-orphan")

    parent_com = db.relationship("Company", back_populates="children_op")

    # By default, operators that have been instantiated are authenticated
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.Operator_ID

    def __repr__(self):
        return '<Operator %r>' % self.Username
