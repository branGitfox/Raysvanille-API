from sqlalchemy import Column, Integer, String, TIMESTAMP, text, Boolean, ForeignKey, Text, Numeric, UUID,Enum as SQLEnum, values
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Relationship


Base = declarative_base()




class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, nullable=False)
    role_name = Column(String(100), nullable=False)
    pages = relationship('Page', secondary='roles_pages', back_populates="roles")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True, nullable=False)
    page_name = Column(String(100), nullable=False)
    page_path = Column(String(50), nullable=False)
    roles = relationship('Role', secondary='roles_pages', back_populates="pages")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class RolePage(Base):
    __tablename__ = "roles_pages"
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), primary_key=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, server_default="true")
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"), nullable=False)
    role = relationship('Role')

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Customer(Base):
    __tablename__= "customers"
    id = Column(Integer, primary_key=True, nullable=False)
    client_name = Column(String(50), nullable=False)
    phone = Column(Numeric, nullable=True)
    picture_url = Column(Text, nullable=False)
    mailable = Column(Boolean, server_default="true", nullable=False)
    email = Column(String, nullable=False)
    orders = relationship('Orders', back_populates="customer")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Shop(Base):
    __tablename__ = "shop"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    shop_name = Column(String(50), nullable=False, server_default="Paul'Ah Mode")
    devise = Column(String(10), nullable=False, server_default="MGA")
    tva = Column(Integer(), nullable=False, server_default="20")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, nullable=False)
    category_name = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, nullable=False)
    genre_name = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    brand = Column(String(50), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete="CASCADE"),  nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    last_price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    min_stock = Column(Integer, nullable=False)
    tags = relationship('Tag', back_populates='product')
    images = relationship('Images', back_populates='product')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,  server_default=text("now()"))

    # Pour les tags
class Tag(Base):
        __tablename__ = "tags"
        id = Column(Integer, primary_key=True, nullable=False)
        tag_name = Column(String(50), nullable=False)
        quantity = Column(Integer, nullable=False)
        product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete="CASCADE"))
        product = relationship('Product', back_populates='tags')

# Pour les images
class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, nullable=False)
    image_url = Column(Text, nullable=False)
    product = relationship('Product', back_populates='images')
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete="CASCADE"))



from sqlalchemy import Column, Integer, String, Text, CheckConstraint

class Content(Base):
    __tablename__ = "contents"
    __table_args__ = (CheckConstraint("id = 1", name="single_row_content"),)

    id = Column(Integer, primary_key=True)
    surtitre = Column(String, nullable=False)
    titre_principale = Column(String, nullable=False)
    deck = Column(String, nullable=False)
    recit_narratif = Column(Text, nullable=False)
    note_territoir = Column(Text, nullable=False, default="")
    message_annonce = Column(String, nullable=False)
    text_bouton_action = Column(String, nullable=False)
    kicker = Column(String, nullable=False)
    accroche = Column(String, nullable=False)
    sous_titre = Column(String, nullable=False)
    num_whatsapp = Column(String, nullable=False)
    email = Column(String, nullable=False)
    ville = Column(String, nullable=False)

 # model pour les commandes
class Orders(Base):
     __tablename__ = "orders"
     id = Column(Integer, primary_key=True)
     phone = Column(String, nullable=False)
     code = Column(String, unique=True, nullable=False)
     customer_name = Column(String, nullable=False)
     city = Column(String, nullable=False)
     description = Column(Text, nullable=True)
     localisation = Column(String, nullable=False)
     total_purchase = Column(Integer, nullable=False)
     status = Column(String, nullable=False)
     items= relationship('OrderItem', back_populates="order")
     customer_id = Column(Integer, ForeignKey('customers.id', ondelete="CASCADE"), nullable=False)
     customer = relationship('Customer', back_populates="orders")
     created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False)



class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    tag = Column(String, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable =False)
    order = relationship("Orders", back_populates = "items")








