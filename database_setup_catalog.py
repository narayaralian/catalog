from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    picture = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'picture': self.picture,
            'id': self.id,
        }


class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True) 
    parentid = Column(Integer, ForeignKey('category.id'))
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    children = relationship("Category", backref=backref('parent', remote_side=[id]))
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'parentid': self.parentid,
            'name': self.name,
            'user': self.user_id,
            'created_on': self.created_on
            
        }


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    picture = Column(String(250))
    categoryid = Column(Integer, ForeignKey('category.id'))
    catalogid = Column(Integer, ForeignKey('catalog.id'))
    userid = Column(Integer, ForeignKey('user.id'))
    category = relationship(Category, backref=backref('items', uselist=True, cascade='delete,all'))
    catalog = relationship(Catalog, backref=backref('items', uselist=True, cascade='delete,all'))
    user = relationship(User, backref=backref('items', uselist=True, cascade='delete,all'))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'picture': self.picture,
            'categoryid': self.categoryid,
            'catalogid': self.catalogid,
            'userid': self.userid
            
        }


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)