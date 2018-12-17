#!/usr/bin/env python3
#
# Item Catalog Project, Udacity Full Stack Web Development Nanodegree
# Nara Yaralyan, narayaralian@yahoo.com


from flask import Flask, render_template, request,\
    redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, and_, asc, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup_catalog import Base, Catalog, Item, User, Category
from flask import session as login_session
from werkzeug.utils import secure_filename
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import os
from flask import make_response
import requests
import datetime

# IMAGE UPLOAD

# upload folder and allowed file extensions
UPLOAD_FOLDER = 'static/image/'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])
# datetime is used to create a unique file name for an image
format = "%Y-%m-%dT%H:%M:%S"
now = datetime.datetime.utcnow().strftime(format)
# default image
defaultimg = 'placeholder.jpeg'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"


# Connect to Database and create a database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

session = scoped_session(sessionmaker(bind=engine))


# LOGIN
# Create an anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Login with your Google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius: 150px;
                    -webkit-border-radius: 150px;
                    -moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# FILE UPLOAD ################
# Check if file extension is allowed: for uploading files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file):
    format = "%Y-%m-%dT%H:%M:%S"
    now = datetime.datetime.utcnow().strftime(format)

    if file and allowed_file(file.filename):
        filename = now + '_' + file.filename
        filename = secure_filename(filename)
        file.save(os.path.join(
            app.root_path, app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = defaultimg
    return filename


# LIST ALL CATEGORIES ################
def listAllCategory():
    categories = session.query(Category).order_by(Category.parent).all()
    return categories


# CATALOGS, ITEMS AND CATEGORIES #############
# JSON APIs to view Catalog Data
# JSON: list items in a catalog
@app.route('/catalog/<int:catalogid>/items/JSON')
@app.route('/catalog/<int:catalogid>/JSON')
def catalogItemJSON(catalogid):
    catalog = session.query(Catalog).filter_by(id=catalogid).one()
    items = session.query(Item).filter_by(
        catalogid=catalogid).all()
    return jsonify(Items=[i.serialize for i in items])


# JSON: detailed view for an item
@app.route('/catalog/<int:catalogid>/items/<int:itemid>/JSON')
@app.route('/catalog/<int:catalogid>/<int:itemid>/JSON')
def itemJSON(catalogid, itemid):
    item = session.query(Item).filter_by(id=itemid).one()
    return jsonify(Item=item.serialize)


# JSON: show all catalogs
@app.route('/catalog/JSON')
def catalogJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs=[r.serialize for r in catalogs])


# JSON: show items by categories
@app.route('/catalog/category/<int:categoryid>/JSON')
def itemsByCatJSON(categoryid):
    # Query for all child categories of the parent == categoryid
    categoryall = session.query(Category).filter_by(parentid=categoryid).all()
    items = session.query(Item).filter(
        or_(Item.categoryid == categoryid, Item.categoryid.in_(
            [c.id for c in categoryall]))).outerjoin(Catalog).all()
    return jsonify(Items=[i.serialize for i in items])


# MANAGE CATALOGS #############
# Show all catalogs
@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    categories = listAllCategory()
    if 'username' not in login_session:
        return render_template('publiccatalogs.html',
                               catalogs=catalogs, categories=categories)
    else:
        return render_template('catalogs.html',
                               catalogs=catalogs, categories=categories)


# Create a new catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        user_id = login_session['user_id']
        name = request.form.get('name')
        description = request.form.get('description')
        file = request.files.get('file')
        # Check if all required fields are filled out properly
        if not name:
            flash('Catalog name is required.')
            return redirect(url_for('newCatalog'))
        # Upload photo
        filename = upload_file(file)
        # Create a new catalog
        newCatalog = Catalog(name=name, description=description,
                             picture=filename, user_id=user_id)
        session.add(newCatalog)
        session.commit()
        flash('You have successfully created a new catalog')
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newCatalog.html')


# Edit a catalog: edited
@app.route('/catalog/<int:catalogid>/edit/', methods=['GET', 'POST'])
def editCatalog(catalogid):
    editedCatalog = session.query(
        Catalog).filter_by(id=catalogid).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCatalog.user_id != login_session['user_id']:
        return "<script>\
                    function myFunction(){\
                        alert(\
                        'You are not authorized to edit this catalog.');}\
                </script>\
                <body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
        if request.form['description']:
            editedCatalog.description = request.form['description']
        if request.files.get('file'):
            file = request.files.get('file')
            # Upload photo
            filename = upload_file(file)
            editedCatalog.picture = filename
        session.add(editedCatalog)
        session.commit()
        flash('You have Successfully Edited %s' % editedCatalog.name)
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('editCatalog.html', catalog=editedCatalog)


# Delete a catalog
@app.route('/catalog/<int:catalogid>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalogid):
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalogid).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catalogToDelete.user_id != login_session['user_id']:
        return "<script>\
                    function myFunction() {\
                        alert(\
                        'You are not authorized to delete this catalog.');}\
                 </script>\
                 <body onload='myFunction()'>"
    if request.method == 'POST':
        delete = request.form['delete']
        if delete == 'yes':
            session.delete(catalogToDelete)
            session.commit()
            flash('%s Successfully Deleted' % catalogToDelete.name)
            return redirect(url_for('showCatalogs'))
        else:
            flash('Deletion has been canceled')
            return redirect(url_for('showCatalogs'))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)


# MANAGE ITEMS #############
# Show items in the catalog
@app.route('/catalog/<int:catalogid>/')
@app.route('/catalog/<int:catalogid>/items/')
def showItems(catalogid):
    catalog = session.query(Catalog).filter_by(id=catalogid).one()
    creator = getUserInfo(catalog.user_id)
    items = session.query(Item).filter_by(
        catalogid=catalogid).outerjoin(Category).all()
    categories = listAllCategory()
    if 'username' not in login_session \
            or creator.id != login_session['user_id']:
        return render_template('publicitems.html', items=items,
                               catalog=catalog, creator=creator,
                               categories=categories)
    else:
        return render_template('items.html',
                               items=items, catalog=catalog,
                               creator=creator, categories=categories)


# Create a new item
@app.route('/catalog/<int:catalogid>/items/new/', methods=['GET', 'POST'])
def newItem(catalogid):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalogid).one()
    if login_session['user_id'] != catalog.user_id:
        return "<script>\
                    function myFunction() {\
                        alert(\
                        'You are not authorized \
                        to add items to this catalog.');}\
                 </script>\
                 <body onload='myFunction()'>"
    category = session.query(Category).all()
    if request.method == 'POST':
        if request.form.get('name'):
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')
            # Upload an image
            file = request.files.get('file')
            filename = upload_file(file)
            newItem = Item(name=name, description=description,
                           price=price, picture=filename,
                           categoryid=category, catalogid=catalogid,
                           userid=catalog.user_id)
            session.add(newItem)
            session.commit()
            flash('New Item %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showItems', catalogid=catalogid))
        else:
            flash('Item name is required.')
            return redirect(url_for('newItem', catalogid=catalogid))
    else:
        return render_template('newItem.html',
                               catalog=catalog, category=category)


# Edit an item
@app.route('/catalog/<int:catalogid>/items/<int:itemid>/edit',
           methods=['GET', 'POST'])
def editItem(catalogid, itemid):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=itemid).one()
    catalog = session.query(Catalog).filter_by(id=catalogid).one()
    if login_session['user_id'] != catalog.user_id:
        return "<script>\
                    function myFunction() {\
                        alert(\
                            'You are not authorized to edit\
                            items to this catalog.\
                            Please create your own catalog\
                            in order to edit items.'\
                            );}\
                  </script>\
                  <body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['category']:
            editedItem.categoryid = request.form['category']
        if request.files.get('file'):
            file = request.files.get('file')
            # Upload photo
            filename = upload_file(file)
            editedItem.picture = filename
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showItems', catalogid=catalogid))
    else:
        category = listAllCategory()
        return render_template('editItem.html', catalog=catalog,
                               category=category, item=editedItem)


# Delete an item
@app.route('/catalog/<int:catalogid>/items/<int:itemid>/delete',
           methods=['GET', 'POST'])
def deleteItem(catalogid, itemid):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalogid).one()
    itemToDelete = session.query(Item).filter_by(id=itemid).\
        outerjoin(Category).one()
    if login_session['user_id'] != catalog.user_id:
        return "<script>\
                    function myFunction() {\
                        alert(\
                            'You are not authorized\
                            to delete items to this catalog.\
                            Please create your own catalog\
                            in order to delete items.');}\
                  </script>\
                  <body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['delete'] == 'yes':
            session.delete(itemToDelete)
            session.commit()
            flash('Item Successfully Deleted')
            return redirect(url_for('showItems', catalogid=catalogid))
        else:
            flash('Deletion has been canceled')
            return redirect(url_for('showItems', catalogid=catalogid))
    else:
        return render_template('deleteItem.html',
                               item=itemToDelete, catalog=catalog)


# Show items by categories
@app.route('/catalog/category/<int:categoryid>/<string:categoryname>')
def showItemsByCat(categoryid, categoryname):
    # Query for all child categories of the parent == categoryid
    categoryall = session.query(Category).filter_by(parentid=categoryid).all()
    items = session.query(Item).filter(or_(
        Item.categoryid == categoryid, Item.categoryid.in_(
            [c.id for c in categoryall]))).outerjoin(Catalog).all()
    categories = listAllCategory()
    return render_template('itemsByCat.html',
                           items=items, categoryname=categoryname,
                           categoryall=categoryall, categories=categories)


# Detailed view for an item
@app.route('/catalog/<int:catalogid>/<int:itemid>/')
def showItemDetail(catalogid, itemid):
    item = session.query(Item).filter_by(id=itemid).\
        outerjoin(Category, Catalog, User).first()
    categories = listAllCategory()
    return render_template('detailsItem.html',
                           item=item, categories=categories)


# MANAGE CATEGORIES
# Create a new category
@app.route('/catalog/categories/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    user_id = login_session['user_id']
    if request.method == 'POST':
        if request.form['name']:
            name = request.form['name']
            if request.form['category']:
                parent = request.form['category']
            parent = None
            # Create a new category
            new = Category(name=name, parentid=parent, user_id=user_id)
            session.add(new)
            session.commit()
            flash('You have successfully created a new category')
            return redirect(url_for('newCategory'))
        else:
            # Check if all required fields are filled out properly
            flash('Category name is required.')
            return redirect(url_for('newCategory'))
    else:
        category = session.query(Category).all()
        return render_template('newCategory.html',
                               user_id=user_id, category=category)


# Edit a category
@app.route('/catalog/<int:categoryid>/editcategory/',
           methods=['GET', 'POST'])
def editCategory(categoryid):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=categoryid).one()
    if login_session['user_id'] != category.user_id:
        return "<script>\
                    function myFunction() {\
                        alert(\
                            'You are not authorized to edit this category.');}\
                  </script>\
                  <body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
        if request.form['category']:
            category.parentid = request.form['category']
        else:
            category.parentid = None
        session.add(category)
        session.commit()
        flash('You\'ve successfully updated %s' % category.name)
        return redirect(url_for('newCategory'))
    else:
        allcategories = listAllCategory()
        return render_template('editCategory.html',
                               category=category, allcategories=allcategories)


# Delete category
@app.route('/catalog/<int:categoryid>/deletecategory/',
           methods=['GET', 'POST'])
def deleteCategory(categoryid):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=categoryid).one()
    if login_session['user_id'] != category.user_id:
        return "<script>\
                    function myFunction() {\
                        alert(\
                        'You are not authorized to delete this category.');}\
                  </script>\
                  <body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['delete'] == 'yes':
            session.delete(category)
            session.commit()
            flash('You\'ve successfully deleted %s' % category.name)
            return redirect(url_for('newCategory'))
        else:
            flash('Deletion has been canceled')
            return redirect(url_for('newCategory'))
    else:
        return render_template('deleteCategory.html', category=category)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalogs'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalogs'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
