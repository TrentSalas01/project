from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


@login_manager.user_loader
def load_user(user_id):
    """
    Function to load the user
    @param user_id: the user id that is being loaded
    """
    return User.query.get(int(user_id))


users_in_community = db.Table('users_in_community',
                              db.Column('community_id', db.Integer,
                                        db.ForeignKey('communities.id')),
                              db.Column('user_id', db.Integer,
                                        db.ForeignKey('user.id'))
                              )
likes_on_posts = db.Table('likes_on_posts',
                          db.Column('post_id', db.Integer,
                                    db.ForeignKey('posts.id')),
                          db.Column('user_id', db.Integer,
                                    db.ForeignKey('user.id'))
                          )
dislikes_on_posts = db.Table('dislikes_on_posts',
                             db.Column('post_id', db.Integer,
                                       db.ForeignKey('posts.id')),
                             db.Column('user_id', db.Integer,
                                       db.ForeignKey('user.id'))
                             )


# TODO: Move all class files into this file and setup models to initialize DB tables etc.
#   Currently having issues with import loop ie importing db from index and then importing User from models
#   Restructuring should resolve this issue
#   Need help from Dr. Layman regarding the best way to go about this (?)


class User(db.Model, UserMixin):
    """
    Class for the User
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean)
    profile_picture = db.Column(db.String)
    bio = db.Column(db.VARCHAR)
    posts = db.relationship('Posts', backref='author', lazy=True)
    collections = db.relationship(
        'Collections', backref='collectionAuthor', lazy=True, cascade="all, delete-orphan")

    def __init__(self, username, email, password, admin):
        """
        Constructor for the user Class
        @param username: username of the user
        @param email: email of the user
        @param password: password of the user
        @param admin: True if admin; false
        """
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email
        self.admin = admin

    def verify_password(self, pwd):
        """
        Function to verify password
        @param pwd: password being verified
        @return: returns True or False
        """
        return check_password_hash(self.password, pwd)

    def addCollection(self, collection):
        """
        Function to add a collection
        @param collection: collection being added
        """
        self.collections_list.append(collection)
        db.session.commit()

    def removeCollection(self, collection):
        """
        Function to remove a collection
        @param collection: collection being removed
        """
        if collection in self.collections_list:
            # print(self.collections_list)
            self.collections_list.remove(collection)
            # print(self.collections_list)
            db.session.commit()

    def __repr__(self):
        """
        Printable representation function
        """
        return f'<User {self.username}, {self.email}, {self.password}, {self.collections}>'


class CollectionItem(db.Model):
    """
    CollectionItem creates the Items that belong to collections, and are categorized by user, collection, and community.
    They have a photo, description, and name.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    desc = db.Column(db.String)
    photo = db.Column(db.String)
    community_id = db.Column(db.Integer, db.ForeignKey(
        'communities.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey(
        'collections.id'), nullable=False)

    def __init__(self, user, community, photo, desc, collection, name):
        """
        @param user: The User that is creating the item
        @param community: the community that the item and associated collection belongs to
        @param photo: the file location of the image for the item
        @param desc: the text description for the item
        @param collection: the collection that the item belongs to
        @param name: the name of the item
        """
        self.collection_id = collection
        self.user = user
        self.community_id = community
        self.photo = photo
        self.desc = desc
        self.name = name

    def __repr__(self):
        """
        Printable representation function
        """
        return f'<CollectionItem {self.name}, {self.user}, {self.community_id}, {self.collection_id}>'

    def getUser(self):
        """
        Returns user of the item
        @return: user
        """
        return User.query.filter_by(id=self.user).first()


class Collections(db.Model):
    """
    Collections creates a collection for a user. A collection contains the items that a user creates. A collection
    belongs to a community, and cannot exist without the original community. A collection has a name and a description,
    set by the user.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    desc = db.Column(db.String)
    items = db.relationship(
        'CollectionItem', backref='Collections', lazy=True, cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    community_id = db.Column(
        db.Integer, db.ForeignKey('communities.id'), nullable=False)
    kind = db.Column(db.String)

    def __init__(self, name, desc, user_id, community_id):
        """
        @param name:The name of the collection
        @param desc: The description of the collection
        @param user_id:The ID of the user who owns the collection
        @param community_id: The community ID that the collection is a part of
        """
        self.name = name
        self.desc = desc
        self.user_id = user_id
        self.community_id = community_id
        self.items = []
        self.kind = "collection"

    def __repr__(self):
        """
        Printable representation function
        """
        return f'<Collection {self.name}, {self.items}, {self.community_id}>'

    def getId(self):
        """
        Returns the user ID of the item
        :return: the associated user id of the collection
        """
        return self.user_id


class Communities(db.Model):
    """
    Class for the communities
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)
    desc = db.Column(db.String)
    collections = db.relationship(
        'Collections', backref='communities', lazy=True)
    users = db.relationship(
        'User', secondary=users_in_community, backref='users')

    def __init__(self, name, desc):
        """
        Constructor class cor communities class
        @param name: name of the community
        @param desc: community's description
        """
        self.name = name
        self.desc = desc
        self.url = name.lower().translate({ord(i): None for i in "'.,;:"}).replace('"', "").translate(
            {ord(i): "_" for i in " -"})
        self.posts = []
        self.collections = []
        self.users = []

    def getCollections(self):
        """
        Returns a list of collections in the community
        :return: list of references to collections in the community
        """
        return self.collections

    def addCollection(self, collection):
        """
        Adds a collection to the community
        :return: none
        """
        if collection not in self.collections:
            self.collections.append(collection)
            db.session.commit()

    def removeCollection(self, collection):
        """
        Removes a collection from the community
        :return: none
        """
        if collection in self.collections:
            self.collections.remove(collection)
            db.session.commit()

    def getPosts(self):
        """
        Returns all posts in the community
        :return: list of references to posts in the community
        """
        posts = Posts.query.filter_by(community_id=self.id).all()
        print(posts)
        return posts

    def addPost(self, post):
        """
        Adds a post to the community
        :return: none
        """
        if post not in self.posts:
            self.posts.append(post)
            db.session.commit()

    def removePost(self, post):
        """
        Removes a post from the community
        :return: none
        """
        if post in self.posts:
            self.posts.remove(post)
            db.session.commit()

    def userHasJoined(self, user_id):
        """
        Returns a boolean if the user joined the given community
        :param user_id: a user to locate in the list of the community's followers
        :return: boolean (True if user joined community, else false)
        """
        if user_id in self.users:
            return True
        return False

    def addUser(self, user_id):
        """
        Adds a user to the community
        :param user_id: a user id to locate in the list of the community's followers
        :return: none
        """
        if not self.userHasJoined(user_id):
            self.users.append(user_id)
            db.session.commit()

    def removeUser(self, user_id):
        """
        Removes a user from the community
        :param user_id: a user id to locate in the list of the community's followers
        :return: none
        """
        if self.userHasJoined(user_id):
            self.users.remove(user_id)

            db.session.commit()

    def getUsers(self):
        """
        Getter to get users
        @return: returns the users
        """
        return self.users

    def memberCount(self):
        """
        Counts the number of members
        @returns the number of members
        """
        return len(self.users)

    def setName(self, name):
        """
        Setter for the name of the community. Also adjusts the url-name
        :return: none
        """
        self.name = name
        self.url = name.lower().translate({ord(i): None for i in "'.,;:"}).replace('"', "").translate(
            {ord(i): "_" for i in " -"})
        db.session.commit()

    def __repr__(self):
        """
        Printable representation function
        """
        return f'<Community "{self.url}">'


class Photos(db.Model):
    """
    Class for the photos
    """
    id = db.Column(db.Integer, primary_key=True)
    photo_blob = db.Column(db.String)


class Posts(db.Model):
    """
    Class for the  posts
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.String)
    timestamp = db.Column(db.String)
    meta = db.Column(db.String)
    comments = db.Column(db.String)
    item_id = db.Column(db.Integer)
    community_id = db.Column(db.Integer)
    likes = db.relationship(
        'User', secondary=likes_on_posts, backref='usersWhoLiked')
    dislikes = db.relationship(
        'User', secondary=dislikes_on_posts, backref='usersWhoDisliked')
    kind = db.Column(db.String)

    def __init__(self, author_id, title, body, community_id, item_id=None):
        """
        Constructor for the posts class
        @param author_id: id of the author
        @param title: title of the post
        @param body: body of the post
        @param community_id: the id of the community
        @param item_id: the id of the item in the post
        """
        self.author_id = author_id
        self.title = title
        self.body = body
        self.community_id = community_id
        self.timestamp = str(datetime.datetime.now())
        self.likes = []
        self.dislikes = []
        self.item_id = item_id
        self.kind = "post"

    def getAuthor(self):
        """
        Getter to get the author of the post
        @return: returns the author
        """
        return User.query.filter_by(id=self.author_id).first()

    def getCommunity(self):
        """
        Getter to get the community of the post
        @return: returns the community the post is in
        """
        return Communities.query.filter_by(id=self.community_id).first()

    def setBody(self, body):
        """
        Setter to set the body
        @param body: body that is being updated
        """
        self.body = body

    def getComments(self):
        """
        Getter to get comments of a post
        @return: returns the comments of a given post
        """
        return Comments.query.filter_by(post_id=self.id).all()

    def getCommentCount(self):
        """
        Calculates number of comments and returns it in a formatted string
        @return: returns formatted string indicating number of comments on the post
        """
        comments = Comments.query.filter_by(post_id=self.id).all()
        if comments is None or len(comments) == 0:
            return "No comments"
        elif len(comments) == 1:
            return "1 comment"
        else:
            return str(len(comments)) + " comments"

    def clearComments(self):
        """
        function to delete comments on a post
        """
        # deletes all comments under a post; should only be called prior to deleting the post
        comments = self.getComments()
        for i in comments:
            db.session.delete(i)
        db.session.commit()

    def getRawTimestamp(self):
        """
        Getter to get the raw timestamp of a post
        @return: returns the raw timestamp for the post
        """
        return self.timestamp

    def getTimestamp(self):
        """
        Getter to get the formatted timestamp of a post
        @return: returns the formatted timestamp for the post
        """
        now = str(datetime.datetime.now()).split(" ")
        post_time_for_eval = self.timestamp.split(" ")
        if now[0] == post_time_for_eval[0]:
            return "at " + post_time_for_eval[1].split(".")[0]
        else:
            return "on " + post_time_for_eval[0]

    def __repr__(self):
        """
        Printable representation function
        """
        return f'<Post #{self.id} in Community "{self.getCommunity().url}">'


class Comments(db.Model):
    """
    Class for the comments of a post
    """
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    text = db.Column(db.String)
    timestamp = db.Column(db.String)
    meta = db.Column(db.String)
    locked = db.Column(db.Boolean)

    def __init__(self, author_id, text, post_id):
        """
        Constructor for the comments class
        @param author_id: id of the post's author
        @param text: the text of the comment
        @param post_id: id of the post being commented on
        """
        self.author_id = author_id
        self.post_id = post_id
        self.text = text
        self.timestamp = str(datetime.datetime.now())
        self.locked = False

    def getAuthor(self):
        """
        Getter to get author
        @return: returns the author
        """
        return User.query.filter_by(id=self.author_id).first()

    def getPost(self):
        """
        getter to get the post
        @return: returns the post
        """
        return Posts.query.filter_by(id=self.post_id).first()

    def isLocked(self):
        """
        Boolean to decide if it is locked
        @return: returns True or False
        """
        return self.locked

    def setText(self, text):
        """
        Setter to set the text
        @param text: text being set
        """
        self.text = text
        db.session.commit()

    def lockComment(self):
        """
        Locks the comment. Used instead of deletion when an admin removes a comment.
        """
        self.text = "This comment has been removed by an administrator."
        self.locked = True
        db.session.commit()

    def getRawTimestamp(self):
        """
        Getter to get the raw timestamp of a comment
        @return: returns the raw timestamp for the comment
        """
        return self.timestamp

    def getTimestamp(self):
        """
        Getter to get the formatted timestamp of a comment
        @return: returns the formatted timestamp for the comment
        """
        now = str(datetime.datetime.now()).split(" ")
        post_time_for_eval = self.timestamp.split(" ")
        if now[0] == post_time_for_eval[0]:
            return "at " + post_time_for_eval[1].split(".")[0]
        else:
            return "on " + post_time_for_eval[0]

    def __repr__(self):
        """
        Printable representation function
        """
        return f'<comment #{self.id} under post #{self.post_id} in community "{self.getCommunity().url}">'
