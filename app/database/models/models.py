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
    client_name = Column(String(50), nullable=False )
    is_promoted = Column(Boolean, nullable=False, server_default="false")
    notes = Column(Text, nullable=True)
    phone = Column(Numeric, nullable=False)
    cin = Column(Numeric, nullable=False)
    picture_url = Column(Text, nullable=False)
    is_reseller = Column(Boolean, nullable=False, server_default="false")
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
    id = Column(Integer, primary_key=True, nullable=False)
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
        product_id = Column(Integer, ForeignKey('products.id', ondelete="CASCADE"))
        product = relationship('Product', back_populates='tags')

# Pour les images
class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, nullable=False)
    image_url = Column(Text, nullable=False)
    product = relationship('Product', back_populates='images')
    product_id = Column(Integer, ForeignKey('products.id', ondelete="CASCADE"))






