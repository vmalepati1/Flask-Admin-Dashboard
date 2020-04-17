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

    children_assoc = db.relationship("CategoryCompanyAssignment", back_populates="parent_com", cascade="all, delete-orphan")
    children_deliv = db.relationship("CompanyDelivery", back_populates="parent_com", cascade="all, delete-orphan")
    children_time = db.relationship("CompanyTimetable", back_populates="parent_com", cascade="all, delete-orphan")
    children_op = db.relationship("Operator", back_populates="parent_com", cascade="all, delete-orphan")
    
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
        return '<Company Delivery %r>' % self.delivery_id

class CompanyTimetable(db.Model):
    timetable_id = db.Column(db.Integer, primary_key=True)
    Company_ID = db.Column(db.Integer, db.ForeignKey('company.Company_ID'))
    weekday = db.Column(db.Integer)
    open_time = db.Column(db.TIME)
    close_time = db.Column(db.TIME)

    parent_com = db.relationship("Company", back_populates="children_time")

    def __repr__(self):
        return '<Company Timetable %r>' % self.timetable_id
    
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
