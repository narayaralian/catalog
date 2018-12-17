from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup_catalog import Base, Catalog, Item, User, Category

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Categories for a Christmas Catalogue
category1 = Category(name="Christmas", user_id=1) # a parent category for other Christmas categories
category2 = Category(name="Books", user_id=1)
category3 = Category(name="Greeting Cards", user_id=1)
category4 = Category(name="Decoration", user_id=1)
category5 = Category(name="Gifts", user_id=1)
category6 = Category(name="Fantasy", user_id=1, parentid=2)
category7 = Category(name="Books for Kids", user_id=1, parentid=2)
category8 = Category(name="Detective Fiction", user_id=1, parentid=2)
category9 = Category(name="Classic Novels", user_id=1, parentid=2)

# Create dummy user
User1 = User(id = 1, name="Nara Yaralyan", email="narayaralian@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Christmas Gifts Catalogue
catalog1 = Catalog(user_id=1, name="Madi's Christmas Boutique", description="Decorate your Holiday Season with our amazing handmade crafts and Christmas gifts!", picture="madiboutique.jpeg")

session.add(catalog1)
session.commit()

Item1 = Item(userid=1, name="Happy Christmas Greeting Card", description="This vibrant holiday card features golden foil stars and spots on the front against a rich red background.",
                     price="$3.50", picture="greetingcard.jpeg", category=category3, catalog=catalog1)

session.add(Item1)
session.commit()


Item2 = Item(userid=1, name="Merry Christmas Greeting Card", description="Santa and two funny Snowmen wishing Merry Christmas to your loved ones.",
                     price="$2.50", picture="greetingcard1.jpeg", category=category3, catalog=catalog1)

session.add(Item2)
session.commit()

Item3 = Item(userid=1, name="A Christmas Carol by Charles Dickens", description="An old, bitter man named Ebenezer Scrooge is visited by three ghosts who take him on a journey through Christmases past, present, and future.",
                     price="$10.50", picture="greetingcard1.jpeg", category=category2, catalog=catalog1)

session.add(Item3)
session.commit()

Item4 = Item(userid=1, name="A Lot Like Christmas by Connie Willis", description=" Twelve beautifully crafted holiday stories.",
                     price="$25.50", picture="placeholder.jpeg", category=category2, catalog=catalog1)

session.add(Item4)
session.commit()

Item5 = Item(userid=1, name="A Happy Snowman Mug ", description="Festive Christmas gift: Get into the spirit of the festive season with these hand-painted red mugs.",
                     price="$25.50", picture="mug.jpeg", category=category5, catalog=catalog1)

session.add(Item5)
session.commit()

Item6 = Item(userid=1, name="Three White Snowman Decoration", description="This cutest Snowman family would love to join your Christmas party!",
                     price="$25.50", picture="snowmandecor.jpeg", category=category4, catalog=catalog1)

session.add(Item6)
session.commit()

Item7 = Item(userid=1, name="Christmas Novelty Lights", description="Clear, random sparkle bulbs offer a festive glowty!",
                     price="$24.98", picture="placeholder.jpeg", category=category4, catalog=catalog1)

session.add(Item7)
session.commit()

Item8 = Item(userid=1, name="Happy Holidays Gift Basket", description="Lemon cookies, dark chocolate marshmallows, caramel corn, truffles, milk chocolate caramels, peppermint sticks, hot cocoa and more...",
                     price="$50.98", picture="placeholder.jpeg", category=category5, catalog=catalog1)

session.add(Item8)
session.commit()

Item9 = Item(userid=1, name="The Santa Claus Game", description="When the holidays come this game will be a great way for children and adults to have some fun and cut loose!",
                     price="$19.99", picture="placeholder.jpeg", category=category5, catalog=catalog1)

session.add(Item9)
session.commit()


# Book Catalogue
catalog2 = Catalog(user_id=1, name="Book Catalog", description="A simple catalog of the books I love.", picture="bookcatalog.jpeg")

session.add(catalog2)
session.commit()


Item1 = Item(userid=1, name="Harry Potter and the Philosopher's Stonene by J. K. Rowling", description="The first novel in the Harry Potter series, it follows Harry Potter, a young wizard who discovers his magical heritage on his eleventh birthday...",
                     price="$19.99", picture="harrypotter.jpeg", category=category6, catalog=catalog2)

session.add(Item1)
session.commit()

Item2 = Item(userid=1, name="Winnie-the-Pooh  by  A. A. Milne", description="People say nothing is impossible, but I do nothing every day.",
                     price="$19.99", picture="puh.jpg", category=category7, catalog=catalog2)

session.add(Item2)
session.commit()

Item3 = Item(userid=1, name="Murder on the Orient Express by Agatha Christie ", description="A detective novel by British writer Agatha Christie featuring the Belgian detective Hercule Poirot.",
                     price="$15.99", picture="bookplaceholder.jpeg", category=category8, catalog=catalog2)

session.add(Item3)
session.commit()


Item4 = Item(userid=1, name="The Defense by Vladimir Nabokov", description="The life story of Nabokovs friend Curt von Bardeleben, who committed suicide in 1924. Luzhin, a socially awkward boy, embraces chess to escape from his everyday existence.",
                     price="$21.99", picture="bookplaceholder.jpeg", category=category9, catalog=catalog2)

session.add(Item4)
session.commit()

Item5 = Item(userid=1, name="The Trouble with Goats and Sheep by Joanna Cannon", description="England, 1976. Mrs. Creasy is missing and the Avenue is alive with whispers. The neighbors blame her sudden disappearance on the heat wave, but ten-year-olds Grace and Tilly arent convinced...",
                     price="$25.50", picture="bookplaceholder.jpeg", category=category9, catalog=catalog2)

session.add(Item5)
session.commit()

Item6 = Item(userid=1, name="The Little Prince by Antoine de Saint-Exupery", description="All grown-ups were once children... but only few of them remember it...",
                     price="$25.50", picture="bookplaceholder.jpeg", category=category7, catalog=catalog2)

session.add(Item6)
session.commit()

print "added menu items!"