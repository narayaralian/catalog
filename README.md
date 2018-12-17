# Introduction to Item Catalog

Item Catalog is a simple web application, built with Python, Flask, SQLAlchemy, and SQLite, that allows users to create and manage multiple catalogs of items/products of their choice. 

All users, authorized or unauthorized, can browse through all existing catalogs and items; they can search for items by categories, as well as contact the owners of the catalogs by email.  
The owner's name and email address will show up at the top of the catalog page.  

The application supports user authentication and authorization using OAuth 2.0. Users can login into the system using thier Google accounts to be able to :  
* create and manage (edit, delete) their own catalogs:
    * for each catalog users can provide a name/title, description and a cover image;
* add new items/products to their catalogs; categorize, edit, delete items in their own catalogs:
    * for each item users can provide a name/title, image, description, price, and category;
* create, edit, and delete categories, and assign them to a parent category.

*Note*: Item Catalog is not a real-world project. It was developed for learning purposes as part of the Udacity Full Stack Web Development Nanodegree Program. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

To be able to run Item Catalog, you need a Linux-based virtual machine (VM) installed on your local machine. 
You can use Vagrant and VirtualBox to install and manage the VM: 

1. You will need Git to install the configuration for your VM. If you don't already have Git installed, [download Git from git-scm.com.](http://git-scm.com/downloads) Install the version for your operating system.

2. Download [VirtualBox from virtualbox.org](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1). Install the platform package for your operating system.
  
3. Download [Vagrant from vagrantup.com](https://www.vagrantup.com/downloads.html). Install the version for your operating system.  
If Vagrant is successfully installed, you will be able to run `vagrant --version` in your terminal to see the version number.

### Fetch the Source Code and VM Configuration

**Windows:** Use the Git Bash program (installed with Git) to get a Unix-style terminal.  
**Other systems:** Use your favorite terminal program. 

1. Clone the Vagrantfile from the Udacity Repository: 

From the terminal, run:

    git clone https://github.com/udacity/fullstack-nanodegree-vm

This will create a directory named **fullstack-nanodegree-vm** on your local machine with a vagrantfile you need to be able to run the Item Catalog App.

2. Using the terminal, change directory to fullstack-nanodegree-vm/vagrant/catalog (**cd fullstack-nanodegree-vm/vagrant/catalog**) and clone this repository into that directory.

3. Make sure you are still inside the fullstack-nanodegree-vm directory, if not use the terminal to change directory to fullstack-nanodegree-vm (**cd fullstack-nanodegree-vm**), then type **vagrant up** to launch your virtual machine.

4. Once your VM is up and running, type **vagrant ssh** to login into it.

5. Change to the /vagrant/catalog directory by typing **cd /vagrant/catalog**. You can type **ls** to ensure that you are inside the /catalog directory that contains the following files and directories: 
project_catalog.py, database_setup_catalog.py, additems.py, client_secrets.json,  and two directories named 'templates' and 'static'

6. Now type **python database_setup_catalog.py** to initialize the database.

7. Type **python additems.py** to populate the database with sample catalogs and items.

8. Type **python project_catalog.py** to run the Flask web server. In your browser visit **http://localhost:8000** to view the Item Catalog app. 
After you login with your Google account, you should be able to create, edit and delete your own catalogs, items, and categories.

## Project design

### JSON Endpoints

`/catalog/JSON` - returns JSON of all existing catalogs 

`/catalog/<int:catalogid>/items/JSON` or `/catalog/<int:catalogid>/JSON` - return JSON of all items in a catalog

`/catalog/<int:catalogid>/items/<int:itemid>/JSON` or `/catalog/<int:catalogid>/<int:itemid>/JSON` - return JSON of a particular item

`/catalog/category/<int:categoryid>/JSON` - returns JSON of the items selected by a category

### REST Endpoints

#### Manage Catalogs

`/catalog/` return the list of all existing catalogs 

`/catalog/new/` can be accessed by logged in users to create a new catalog 

`/catalog/<int:catalogid>/edit/` can be accessed by logged in users to edit a selected catalog 

`/catalog/<int:catalogid>/delete/` can be accessed by logged in users to delete a catalog 

#### Manage Items

`/catalog/<int:catalogid>/` or  `/catalog/<int:catalogid>/items/` return the list of all items in the catalog 

`/catalog/category/<int:categoryid>/<string:categoryname>/` returns the list of items selected by a category 

`/catalog/<int:catalogid>/items/new/` can be accessed by logged in users to add a new item to the catalog 

`/catalog/<int:catalogid>/items/<int:itemid>/edit/` can be accessed by logged in users to edit an item 

`/catalog/<int:catalogid>/items/<int:itemid>/delete/` can be accessed by logged in users to delete an item  

`/catalog/<int:catalogid>/<int:itemid>/` returns a detailed view for a particular item 

#### Manage Categories

`/catalog/categories/new/`  allows users to create a new category as well as returns a list of all categories owned by the current user with edit/delete options 

`/catalog/<int:categoryid>/editcategory/`  allows users to edit their own categories 

`/catalog/<int:categoryid>/deletecategory/` allows users to delete their own categories

#### Login

`/gconnect` allows users to sign in with thier Google accounts 

## Deployment

Item Catalog App was developed for learning purposes only and is not intended to be deployed on a live system.

## Built With

* [Python 3](https://www.python.org/)
* [Flask] (http://flask.pocoo.org/)
* [SQLAlchemy] (https://www.sqlalchemy.org/)
* [SQLite](https://www.sqlite.org)
* [HTML] (https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
* [CSS] (https://developer.mozilla.org/en-US/docs/Web/CSS/CSS3)

## Authors

* **Nara Yaralyan** - [LinkedIn](https://www.linkedin.com/in/nara-yaralyan-0b35a833/), [GitHub ] (https://github.com/narayaralian)

## License

This project is licensed under the MIT License.

## Acknowledgments

* This App was developed as part of the Udacity Full-Stack Web Development Program (https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004). Many thanks to the Udacity team for such a great program!
* Free stock photos from [Pexel] (https://www.pexels.com/) are used for this project.
