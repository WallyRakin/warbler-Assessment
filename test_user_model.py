"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from csv import DictReader
from app import db
from models import User, Message, Follows, Likes
from sqlalchemy import and_, or_, not_
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql://test:pass@localhost/warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    # Basic Properties:
    msg_user_creation = 'Checking if a user can be successfully created with valid credentials.'
    msg_no_messages_followers = 'Verifying that a newly created user has no messages and no followers.'
    msg_repr_method = 'Validating the repr method for the User model.'
    msg_uniqueness_constraints = 'Ensuring the User model enforces uniqueness constraints for usernames and emails.'

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        # with open('generator/users.csv') as users:
        #     db.session.bulk_insert_mappings(User, DictReader(users))

        # with open('generator/messages.csv') as messages:
        #     db.session.bulk_insert_mappings(Message, DictReader(messages))

        # with open('generator/follows.csv') as follows:
        #     db.session.bulk_insert_mappings(Follows, DictReader(follows))

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_user_model(self):
        """Does basic model work?"""
        # Basic Properties:

        # Can a user be successfully created with valid credentials?
        u = User.signup(
            username="testuser",
            password="PASSWORD",
            email="test@test.com",
            image_url=User.image_url.default.arg,
        )

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0,
                         "User should have no messages & no followers")
        self.assertEqual(len(u.followers), 0,
                         "User should have no messages & no followers")

        # Does the repr method for the User model work as expected?
        self.assertEqual(
            u.__repr__(), f"<User #{u.id}: {u.username}, {u.email}>", "The repr method for the User model doesn't work as expected")

        # Does the User model correctly enforce constraints like uniqueness for usernames and emails?
        User.signup(
            username="testuser",
            password="PASSWORD",
            email="test1@test.com",
            image_url=User.image_url.default.arg,
        )
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        User.signup(
            username="testuser1",
            password="PASSWORD",
            email="test@test.com",
            image_url=User.image_url.default.arg,
        )
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_user_authentication(self):
        """Does Authentication work?"""
        # Authentication and Authorization:

        # Does User.create successfully create a new user given valid credentials?
        u = User.signup(
            username="testuser",
            password="PASSWORD",
            email="test@test.com",
            image_url=User.image_url.default.arg,
        )

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        # Does User.authenticate successfully return a user when given a valid username and password?
        self.assertEqual(User.authenticate("testuser", "PASSWORD"), u,
                         "User.authenticate failed to successfully return a user when given a valid username and password")

        # Does User.authenticate fail to return a user when the username is invalid?
        self.assertEqual(User.authenticate(
            "wrong_username", "PASSWORD"), False, "User.authenticate didn't fail to return a user when the username is invalid")

        # Does User.authenticate fail to return a user when the password is invalid?
        self.assertEqual(User.authenticate(
            "testuser", "WRONG_PASSWORD"), False, "User.authenticate didn't fail to return a user when the password is invalid")

        # Does User.signup fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?

        User.signup(username="testuser", password="PASSWORD",
                    email="test1@test.com", image_url=User.image_url.default.arg)

        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        User.signup(username="testuser1", password="PASSWORD",
                    email="test@test.com", image_url=User.image_url.default.arg,)

        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        User.signup(username=None, password="PASSWORD",
                    email="test@test.com", image_url=User.image_url.default.arg,)

        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        with self.assertRaises(ValueError):
            User.signup(username="testuser", password=None,
                        email="test@test.com", image_url=User.image_url.default.arg,)
        db.session.rollback()

        User.signup(username="testuser", password="PASSWORD",
                    email=None, image_url=User.image_url.default.arg,)

        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        with self.assertRaises(ValueError):
            User.signup(username=None, password=None,
                        email="test@test.com", image_url=User.image_url.default.arg,)
        db.session.rollback()

        with self.assertRaises(ValueError):
            User.signup(username="testuser", password=None,
                        email=None, image_url=User.image_url.default.arg,)
        db.session.rollback()

        User.signup(username=None, password="PASSWORD",
                    email=None, image_url=User.image_url.default.arg,)

        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        with self.assertRaises(ValueError):
            User.signup(username=None, password=None,
                        email=None, image_url=User.image_url.default.arg,)
        db.session.rollback()

        User.signup(username="testuser1", password="PASSWORD",
                    email="test@test.com", image_url=User.image_url.default.arg,)

        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_user_relationships(self):
        """Does User Relationships work?"""
        # User Relationships:
        u1 = User.signup(
            username="testuser1",
            password="PASSWORD",
            email="test1@test.com",
            image_url=User.image_url.default.arg,
        )
        u2 = User.signup(
            username="testuser2",
            password="PASSWORD",
            email="test2@test.com",
            image_url=User.image_url.default.arg,
        )

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        # Can a user successfully follow another user?
        u1.following.append(u2)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly, when u1 tried to follow u2")
        self.assertIn(u2, u1.following,
                      "User cannot successfully follow another user")

        # Does is_following successfully detect when user1 is following user2?
        self.assertEqual(u1.is_following(
            u2), True, "is_following cannot successfully detect when user1 is following user2")

        # Does is_following successfully detect when user1 is not following user2?
        self.assertEqual(u2.is_following(
            u1), False, "is_following cannot successfully detect when user1 is not following user2")

        # Does is_followed_by successfully detect when user1 is followed by user2?
        self.assertEqual(u2.is_followed_by(
            u1), True, "is_followed_by cannot successfully detect when user1 is followed by user2")

        # Does is_followed_by successfully detect when user1 is not followed by user2?
        self.assertEqual(u1.is_followed_by(
            u2), False, "is_followed_by cannot successfully detect when user1 is not followed by user2")

        # Can a user successfully unfollow another user?
        u1.following.remove(u2)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly, when u1 tried to unfollow u2")
        self.assertFalse(
            u2 in u1.following, "An error was raised when a user tried to unfollow another user")

    def test_user_profile_management(self):
        """Does User profile management functions work?"""
        # Profile Management:
        u = User.signup(
            username="testuser",
            password="PASSWORD",
            email="test@test.com",
            image_url=User.image_url.default.arg,
        )

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        # Can a user's profile be successfully updated with valid data?
        u.email = "newtest@test.com"
        u.username = "newtestuser"
        u.bio = "new bio"
        u.location = "new location"
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when trying to update user profile.")

        u1 = User.signup(
            username="testuser1",
            password="PASSWORD",
            email="test1@test.com",
            image_url=User.image_url.default.arg,
        )
        u2 = User.signup(
            username="testuser2",
            password="PASSWORD",
            email="test2@test.com",
            image_url=User.image_url.default.arg,
        )
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly!")

        # Does the User model handle attempts to update a profile with invalid data (e.g., a non-unique username or email)?
        u2.username = "testuser1"
        u2.password = "PASSWORD"
        u2.email = "test1@test.com"
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        # Can a user's profile be successfully deleted?
        db.session.delete(u)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when deleting a user.")

    def test_user_messages_and_likes(self):
        """Does User profile management functions work?"""
        # User Messages and Likes:
        u1 = User.signup(
            username="testuser1",
            password="PASSWORD",
            email="test1@test.com",
            image_url=User.image_url.default.arg,
        )
        u2 = User.signup(
            username="testuser2",
            password="PASSWORD",
            email="test2@test.com",
            image_url=User.image_url.default.arg,
        )

        try:
            db.session.commit()
        except Exception as e:
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        msg = Message(text="New Message")
        u1.messages.append(msg)

        try:
            db.session.commit()
        except Exception as e:
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when u1 tried creating a message")

        # Can you retrieve all messages associated with a given user?
        self.assertEqual(len(
            u1.messages), 1, "An error was raised while retrieving all the messages associated with a given user")
        self.assertEqual(len(
            u2.messages), 0, "An error was raised while retrieving all the messages associated with a given user")
        self.assertIn(
            msg, u1.messages, "An error was raised while retrieving all the messages associated with a given user")

        # Can a user like a message?
        new_like = Likes(user_id=u2.id, message_id=msg.id)
        db.session.add(new_like)

        try:
            db.session.commit()
        except Exception as e:
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when u2 tried to like a message posted by u1")

        # Can you retrieve all messages liked by a given user?
        for like in u2.likes:
            liked_messages = [Message.query.filter_by(id=a.message_id).one_or_none()
                              for a in Likes.query.filter_by(user_id=u2.id).all()]
            self.assertIn(like, liked_messages,
                          "Error was raised when trying to retrieve all messages liked by a given user")

        # Can a user unlike a message?
        Likes.query.filter(and_(Likes.user_id == u2.id,
                           Likes.message_id == msg.id)).delete()
        try:
            db.session.commit()
        except Exception as e:
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when u2 tried to remove a like on a post")
