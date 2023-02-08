import os
import random
from .models import User, Communities, Collections, Posts, db, CollectionItem, Comments
from flask_login import login_user, current_user, logout_user, login_required
from flask import current_app as app
from flask import render_template, url_for, flash, redirect, request
from werkzeug.utils import secure_filename
from kollekt.forms import (
    RegistrationForm,
    LoginForm,
    UserForm,
    ItemAddForm,
    CreateCommunityForm,
    DeleteCommunityForm,
    CreatePostForm,
    CreateCommentForm,
    EditPostForm,
    DeletePostForm,
    CreateCollectionForm,
    DeleteItemForm,
)
from werkzeug.utils import secure_filename
import uuid as uuid
import os

UPLOAD_FOLDER = "/kollekt/static/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# from .Components.Community import Community
# from .Components.Collection import CollectionItem


@app.route("/")
def home():
    """Creates a route for the home page"""
    posts = Posts.query.all()[:10]
    usersCommunities = []
    allCommunities = Communities.query.all()
    tempCommunities = allCommunities

    tempUsers = []
    allCollections = Collections.query.all()[:10]
    displayCollections = []

    for i in allCollections:
        if len(i.items) > 1:
            posts.append(i)
    if current_user.is_authenticated:
        for community in allCommunities:
            tempUsers = []
            for i in community.getUsers():
                tempUsers.append(i.username)
            if current_user.username in tempUsers:
                usersCommunities.append(community)
    random.shuffle(posts)
    tempComnames = []
    tempUserComNames = []
    for i in tempCommunities:
        tempComnames.append(i.name)
    for x in usersCommunities:
        tempUserComNames.append(x.name)
    for i in tempComnames:
        if i in tempUserComNames:
            tempCommunities.remove(Communities.query.filter_by(name=i).first())
    sampleCollections = Collections.query.all()
    sampleCommunities = Communities.query.all()
    collectionsCount = len(sampleCollections)
    communitiesCount = len(sampleCommunities)
    postCount = len(posts)
    usersCount = len(User.query.all())
    return render_template(
        "home.html",
        postCount=postCount,
        collectionsCount=collectionsCount,
        communitiesCount=communitiesCount,
        usersCount=usersCount,
        sampleCommunities=sampleCommunities,
        sampleCollections=sampleCollections,
        usersCommunities=usersCommunities,
        allCommunities=tempCommunities,
        posts=posts,
        allCollections=displayCollections,
        User=User,
    )


@app.route("/userProfile")
def userProfile():
    """Creates a route for the user's profile page"""
    users_posts = []
    all_posts = Posts.query.all()
    all_posts.reverse()
    for i in all_posts:
        if i.author_id == current_user.id:
            users_posts.append(i)
    posts = Posts.query.all()
    allCommunities = Communities.query.all()
    usersCommunities = []
    collection_user = current_user.collections
    items_user = []
    if current_user.is_authenticated:

        for i in collection_user:
            for i in i.items:
                items_user.append(i)

        for community in allCommunities:
            userlist = community.getUsers()
            finalUserList = []
            for i in userlist:
                finalUserList.append(i.username)
            if current_user.username in finalUserList:
                usersCommunities.append(community)
                allCommunities.remove(community)
    sampleCollections = Collections.query.all()
    sampleCommunities = Communities.query.all()
    return render_template(
        "test.html",
        sampleCommunities=sampleCommunities,
        sampleCollections=sampleCollections,
        usersCommunities=usersCommunities,
        allCommunities=allCommunities,
        posts=posts,
        user=current_user,
        users_posts=users_posts,
        users_collections=collection_user,
        users_items=items_user,
        currentProfilePic=current_user.profile_picture,
    )


@app.route("/userCommunities/<id>")
@login_required
def commCard(id):
    """
    Creates a route for each user to display joined communities
    @param id: id assigned to user
    """
    posts = Posts.query.all()[:10]
    usersCommunities = []
    allCommunities = Communities.query.all()
    tempCommunities = allCommunities

    tempUsers = []
    allCollections = Collections.query.all()[:10]
    displayCollections = []

    for i in allCollections:
        if len(i.items) > 1:
            posts.append(i)
    if current_user.is_authenticated:
        for community in allCommunities:
            tempUsers = []
            for i in community.getUsers():
                tempUsers.append(i.username)
            if current_user.username in tempUsers:
                usersCommunities.append(community)
    random.shuffle(posts)
    tempComnames = []
    tempUserComNames = []
    for i in tempCommunities:
        tempComnames.append(i.name)
    for x in usersCommunities:
        tempUserComNames.append(x.name)
    for i in tempComnames:
        if i in tempUserComNames:
            tempCommunities.remove(Communities.query.filter_by(name=i).first())
    sampleCollections = Collections.query.all()
    sampleCommunities = Communities.query.all()
    collectionsCount = len(sampleCollections)
    communitiesCount = len(sampleCommunities)
    postCount = len(posts)
    usersCount = len(User.query.all())
    return render_template(
        "commCard.html",
        postCount=postCount,
        collectionsCount=collectionsCount,
        communitiesCount=communitiesCount,
        usersCount=usersCount,
        sampleCommunities=sampleCommunities,
        sampleCollections=sampleCollections,
        usersCommunities=usersCommunities,
        allCommunities=tempCommunities,
        posts=posts,
        allCollections=displayCollections,
        User=User,
    )


@app.route("/logout")
def logout():
    """Creates a route for the logout whcih returns to home"""
    logout_user()
    return redirect(url_for("home"))


@app.route("/userSettings", methods=["GET", "POST"])
@login_required
def userSettings():
    """Creates a route for user setting's page"""
    form = UserForm()
    oldemail = False
    oldusername = False
    oldBio = False
    oldPFP = False
    if form.username.data == "":
        form.username.data = current_user.username
        oldusername = True
    if form.email.data == "":
        form.email.data = current_user.email
        oldemail = True
    if form.bio.data == "":
        form.bio.data = current_user.bio
        oldbio = True
    if form.profile_picture.data == "":
        form.profile_picture.data = current_user.profile_picture
        oldPFP = True
    if form.validate_on_submit():
        user = ""
        if not oldusername:
            user = User.query.filter_by(username=form.username.data).first()
        if not oldemail:
            eml = User.query.filter_by(email=form.email.data).first()
        eml = ""
        if not user and not eml:
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.bio = form.bio.data
            current_user.profile_picture = form.profile_picture.data
        elif user:
            flash("Username already taken", "danger")
            return redirect(url_for("userSettings"))
        elif eml:
            flash("Email already used", "danger")
            return redirect(url_for("userSettings"))
        db.session.commit()
        flash(f"Updated {current_user.username}", "success")

    return render_template("settings.html", form=form)


@app.route("/userCard/<user_id>")
@login_required
def userCard(user_id):
    """creates a route for each user that display's the users information"""
    userInfo = User.query.filter_by(id=user_id).first()
    return render_template("userCard.html", userInfo=userInfo)


@app.route("/community/<url>", methods=["GET", "POST"])
def communityPage(url):
    """creates a route for each commmunity page created by an admin"""
    community = Communities.query.filter_by(url=url).first()
    posts_to_display = []
    all_posts = Posts.query.all()
    all_posts.reverse()
    k = 0
    for j in all_posts:
        k += 1
        if j.community_id == community.id:
            posts_to_display.append(j)
        if k == 5:
            break
    if request.method == "POST":
        if current_user.is_authenticated:
            if request.form["join"] == "Join Community":
                community.addUser(current_user)
            elif request.form["join"] == "Leave Community":
                community.removeUser(current_user)
                for i in Collections.query.filter_by(user_id=current_user.id):
                    if i.community_id == community.id:
                        db.session.delete(i)
                        db.session.commit()

        else:
            return redirect(url_for("login"))
    return render_template(
        "community.html",
        community=community,
        user=current_user,
        posts_to_display=posts_to_display,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """creates a route to login"""
    if current_user.is_authenticated:
        flash(f"Login successful", "success")
        return redirect(url_for("home"))

    form = LoginForm()
    username = form.username.data
    password = form.password.data

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            login_user(user, remember=True)
            flash(f"Login successful {user.username}", "success")
            next_page = request.args.get("next")

            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Wrong Password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", title="Login", form=form)


@app.route("/item/<item_id>", methods=["GET", "POST"])
def item_page(item_id):
    """
    Route for page to display items
    @param item_id: The ID of the item to be displayed
    @return: returns the html for the item page
    """
    item = CollectionItem.query.filter_by(id=item_id).first()
    user_id = item.user
    user_true = User.query.filter_by(id=user_id).first()
    user_name = user_true.username
    collection_id = item.collection_id
    item_collection = Collections.query.filter_by(id=collection_id).first()
    collection_name = item_collection.name

    return render_template(
        "item.html",
        item=item,
        username=user_name,
        collectionName=collection_name,
        user_id=user_id,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    creates a route to register a new user
    @return: either home if registered or register if unsuccesfull
    """
    form = RegistrationForm()
    username = form.username.data
    password = form.password.data
    email = form.email.data

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        eml = User.query.filter_by(email=email).first()
        if not user and not eml:
            user = User(username, email, password, False)
        elif user:
            flash("Username already taken", "danger")
            return redirect(url_for("register"))
        elif email:
            flash("Email already used", "danger")
            return redirect(url_for("register"))
        db.session.add(user)
        db.session.commit()
        flash(f"Registered {user.username}", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/addItem/<collection_id>", methods=["GET", "POST"])
def addNewCollectionItem(collection_id):
    """
    Route for creating a collection item. Also handles file saving
    @param collection_id: The ID of the collection that the item belongs to
    @return: Returns the item page for the new item when it is created, otherwise returns the login page if the user is
    not authenticated
    """
    collection_check = []
    for i in Collections.query.all():
        collection_check.append(i.id)
    if int(collection_id) not in collection_check:
        flash("Collection doesn't exist, Try Again", 'danger')
        return redirect(url_for("home"))
    add_community = Collections.query.filter_by(id=collection_id).first().community_id
    add_collection = Collections.query.filter_by(id=collection_id).first().id
    collection_origin = Collections.query.filter_by(id=collection_id).first()
    all_items = CollectionItem.query.all()
    collection_user = Collections.query.filter_by(id=collection_id).first().user_id
    if current_user.is_authenticated and current_user.id == collection_user:
        c_list = []
        for i in Collections.query.all():
            c_list.append((i.id))
        if int(collection_id) not in c_list:
            flash("Collection Error, Try Again",'danger')
            return redirect(url_for("home"))
        form = ItemAddForm()
        if form.validate_on_submit():
            filename = secure_filename(form.photo.data.filename)
            for i in all_items:
                if i.photo == filename:
                    name, ext = os.path.splitext(filename)
                    name = name + str(len(all_items) + 1)
                    filename = "{name}{ext}".format(name=name, ext=ext)
            basedir = os.path.abspath(os.path.dirname(__file__))
            file_path = os.path.join(app.root_path, "./static", filename)
            file_path = file_path.replace("\\", "/")
            form.photo.data.save(file_path)
            flash("IMAGE UPLOADED!", "danger")
            collection_item = CollectionItem(
                user=current_user.id,
                community=add_community,
                photo=filename,
                desc=form.text.data,
                collection=int(collection_id),
                name=form.name.data,
            )

            db.session.add(collection_item)
            db.session.commit()
            item_collection = Collections.query.filter_by(id=collection_id).first()
            collection_name = item_collection.name
            user_name = current_user.username
            return render_template(
                "item.html",
                title="Your Item",
                item=collection_item,
                filename=filename,
                collectionName=collection_name,
                username=user_name,
            )
        return render_template("addItem.html", title="Add Item", form=form, collection_origin=collection_origin)
    else:
        return redirect(url_for("home"))


@app.route("/adminpage", methods=["GET", "POST"])
def adminpage():
    """
    creates a route for admins to create communities
    @returns: admin page
    """
    if current_user.is_authenticated and current_user.admin:

        form = CreateCommunityForm()
        delform = DeleteCommunityForm()
        allCommunities = Communities.query.all()
        if form.validate_on_submit():
            checkCommunity = Communities.query.filter_by(name=form.name.data).first()
            if checkCommunity:
                flash("Community already exists", "danger")
                return redirect(url_for("adminpage"))
            else:
                community = Communities(name=form.name.data, desc=form.description.data)
                db.session.add(community)
                db.session.commit()
            flash(f"Community Created: {community.name}", "success")
            return redirect(url_for("adminpage"))

        if delform.validate_on_submit():
            checkCommunity = Communities.query.filter_by(
                name=delform.deletename.data
            ).first()
            if checkCommunity:
                postsToDelte = checkCommunity.getPosts()
                for i in postsToDelte:
                    db.session.delete(i)
                collectionsToDelete = checkCommunity.getCollections()
                for i in collectionsToDelete:
                    db.session.delete(i)
                db.session.delete(checkCommunity)
                db.session.commit()
                flash(f"Community Deleted {checkCommunity.name}", "success")
                return redirect(url_for("adminpage"))
            else:
                flash("Community does not exist", "danger")
                return redirect(url_for("adminpage"))
        return render_template(
            "adminpage.html", form=form, delform=delform, allCommunities=allCommunities
        )
    else:
        return redirect(url_for("home"))


@app.route("/collections/create/<community_id>", methods=["GET", "POST"])
def createCollection(community_id):
    """
    Route to create a user collection
    @param community_id: The ID of the community that the collection belongs to
    @return: returns to home when the collection is created
    """
    form = CreateCollectionForm()

    if form.validate_on_submit():
        collection = Collections(
            form.name.data, form.desc.data, current_user.id, community_id
        )
        db.session.add(collection)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("createCollection.html", title="Add Item", form=form)


@app.route("/collections/view/<collection_id>", methods=["GET", "POST"])
def viewCollection(collection_id):
    """
    Route to view a users collection
    @param collection_id: The ID of the collection to view
    @return: returns the html for viewing a collection
    """
    collection = Collections.query.filter_by(id=collection_id).first()
    return render_template("collections.html", collection=collection)


@app.route("/community/<community_url>/<post_id>", methods=["GET", "POST"])
def viewPost(community_url, post_id):
    """
    Creates a route for each post for a user to view
    @param community_url: the the url of the community the post is being viewed in.
    @param post_id: the id of the post being viewed.
    @returns the viewpost template and the values: community.url and post.id
    """
    post_to_view = Posts.query.filter_by(id=post_id).first()
    if post_to_view is None:
        return render_template(
            "viewpost.html", post_to_view=post_to_view, community=None
        )
    community = Communities.query.filter_by(url=community_url).first()
    if (
        post_to_view.getCommunity() is not community
    ):  # if correct id but wrong community, corrects url
        return redirect(
            url_for(
                "viewPost",
                community_url=post_to_view.getCommunity().url,
                post_id=post_id,
            )
        )
    form = CreateCommentForm()
    if form.validate_on_submit():
        new_comment = Comments(
            author_id=current_user.id, text=form.text.data, post_id=post_id
        )
        db.session.add(new_comment)
        db.session.commit()
    comments = Comments.query.filter_by(post_id=post_id).all()
    # clears comment box upon posting; otherwise comment text remains in box
    form.text.data = ""
    return render_template(
        "viewpost.html",
        post_to_view=post_to_view,
        community=community,
        comments=comments,
        form=form,
    )


@app.route("/community/<community_url>/create_post", methods=["GET", "POST"])
def addNewPost(community_url):
    """
    Creates a route for each post for the post to be created
    @param community_url: the the url of the community the post being is stored in.
    @returns the viewpost template and the values: community.url and post.id
    """
    if current_user.is_authenticated:
        community = Communities.query.filter_by(url=community_url).first()
        if community.userHasJoined(current_user) is False:
            flash("Must be part of this community to make a post!", "danger")
            return redirect(url_for("communityPage", url=community_url))
        form = CreatePostForm()
        if form.validate_on_submit():
            if form.body.data == "":  # and form.item_id.data == "":
                flash("Must enter text into the body or attach an item!", "danger")
                return redirect(url_for("addNewPost", community_url=community_url))
            else:
                new_post = Posts(
                    author_id=current_user.id,
                    title=form.title.data,
                    body=form.body.data,
                    community_id=community.id,
                )
                db.session.add(new_post)
                db.session.commit()
                flash(
                    f"Post {new_post.id} created in Community {community.url}",
                    "success",
                )
                return redirect(
                    url_for(
                        "viewPost", community_url=community_url, post_id=new_post.id
                    )
                )
        return render_template("createpost.html", form=form)
    else:
        return redirect(url_for("login"))


@app.route("/community/<community_url>/<post_id>/edit", methods=["GET", "POST"])
def editPost(community_url, post_id):
    """
    Creates a route for each post for a edit method to occur
    @param community_url: the the url of the community the post is being edited in.
    @param post_id: the id of the post being edited.
    @returns the viewpost template and the values: community.url and post.id
    """
    post = Posts.query.filter_by(id=post_id).first()
    if post is None:
        return redirect(url_for("home"))
    if current_user.is_authenticated and post.getAuthor() == current_user:
        form = EditPostForm()
        if form.validate_on_submit():
            if form.body.data == "":  # and form.item_id.data == "":
                flash("Must enter text into the body or attach an item!", "danger")
                return redirect(
                    url_for("editPost", community_url=community_url, post_id=post_id)
                )
            else:
                # post.setLinkedItem(form.item_id.data)
                post.setBody(form.body.data)
                db.session.commit()
                flash(f"Post {post.id} in Community {community_url} edited", "success")
                return redirect(
                    url_for("viewPost", community_url=community_url, post_id=post_id)
                )
        form.body.data = post.body
        return render_template(
            "editpost.html", form=form, community_url=community_url, post_id=post_id
        )
    else:
        return redirect(
            url_for("viewPost", community_url=community_url, post_id=post_id)
        )


@app.route("/community/<community_url>/<post_id>/delete", methods=["GET", "POST"])
def delPost(community_url, post_id):
    """
    Creates a route for each post for a delete method to occur
    @param community_url: the the url of the community the post being deleted is in.
    @param post_id: the id of the post being deleted.
    @returns the viewpost template and the values: community.url and post.id
    """
    post = Posts.query.filter_by(id=post_id).first()
    if post is None:
        return redirect(url_for("home"))
    if current_user.is_authenticated and post.getAuthor() == current_user:
        form = DeletePostForm()
        if form.validate_on_submit():
            if form.submitCancel.data:
                return redirect(
                    url_for("viewPost", community_url=community_url, post_id=post_id)
                )
            elif form.submitConfirm.data:
                post_title = post.title
                post.clearComments()
                db.session.delete(post)
                db.session.commit()
                flash("Post " + post_title + " has been deleted", "danger")
                return redirect(url_for("communityPage", url=community_url))
        return render_template("delpost.html", form=form, post=post)
    else:
        return redirect(
            url_for("viewPost", community_url=community_url, post_id=post_id)
        )


@app.route("/comment/<comment_id>/delete", methods=["GET", "POST"])
def delComment(comment_id):
    """
    Creates a route for each comment for a delete method to occur
    @param comment_id: the id of the comment being deleted
    @returns the viewpost template and the values: community.url and post.id
    """
    comment = Comments.query.filter_by(id=comment_id).first()
    if comment is None:
        return redirect(url_for("home"))
    post = comment.getPost()
    community = post.getCommunity()
    if (
        current_user.is_authenticated
        and comment.getAuthor() == current_user
        and comment.isLocked() is False
    ):
        db.session.delete(comment)
        db.session.commit()
        flash("Comment deleted", "danger")
    # if current_user is admin, lock the post instead of deleting it
    return redirect(url_for("viewPost", community_url=community.url, post_id=post.id))


@app.route("/item/<item_id>/delete", methods=["GET", "POST"])
def delItem(item_id):
    """
    Route to return page for deleting an item. Take the item id to be deleted, and renders html for user's choice
    @param item_id:the id of the item that is being deleted
    @return:Returns html for item if canceled or if the user is
    not the owner of the item, returns home if item is deleted
    """
    item = CollectionItem.query.filter_by(id=item_id).first()
    if item is None:
        return redirect(url_for("home"))
    if item.user == current_user.id:

        form = DeleteItemForm()
        if form.validate_on_submit():
            if form.submitCancel.data:
                return redirect(url_for("item_page", item_id=item_id))
            elif form.submitConfirm.data:
                db.session.delete(item)
                db.session.commit()
                flash("item " + item.name + " has been deleted", "danger")
                return redirect(url_for("home"))
        return render_template(
            "delItem.html", title="Delete Item", form=form, item_id=item_id, item=item
        )
    else:
        return redirect(url_for("item_page", item_id=item_id))


@app.route("/fillDB")
def filldb():
    """
    Route to add items to the database
    @param item_id:None
    @return:Returns to homepage with database items added
    """
    db.drop_all()
    db.create_all()
    db.session.add(User("Admin", "admin@kollekt.com", "testing", True))
    db.session.add(Communities("Watches", "Timepieces"))
    db.session.add(Communities("Shoes", "Gloves for your feet"))
    db.session.add(
        Collections("Admins Shoes", "A collection of all of admins shoes", 1, 2)
    )
    db.session.add(
        Collections("Admins Watches", "A collection of all of admins shoes", 1, 1)
    )
    db.session.commit()
    login_user(User.query.filter_by(id=1).first())
    allCommunities = Communities.query.all()

    return redirect(url_for("home"))


@app.route("/fillDB2")
def filldb2():
    """
    Route to add items to the database (used by Josh
    @return:Returns to homepage with database items added
    """
    db.drop_all()
    db.create_all()
    db.session.add(User("Admin", "admin@kollekt.com", "testing", True))
    community1 = Communities("Watches", "Timepieces")
    db.session.add(community1)
    community2 = Communities("Shoes", "Gloves for your feet")
    db.session.add(community2)
    db.session.commit()
    community1.addUser(User.query.filter_by(id=1).first())
    community2.addUser(User.query.filter_by(id=1).first())
    db.session.add(
        Collections("Admins Shoes", "A collection of all of admins shoes", 1, 2)
    )
    db.session.add(
        Collections("Admins Watches", "A collection of all of admins shoes", 1, 1)
    )
    db.session.commit()
    login_user(User.query.filter_by(id=1).first())

    return redirect(url_for("home"))
