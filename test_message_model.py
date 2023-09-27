
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


class MessageModelTestCase(TestCase):
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

    def test_message_model(self):
        """Test basic message model functionality"""
        # Basic Properties:
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

        m = Message(text="Hello World")

        # Can a message be successfully created with valid content and associated with a user?
        u.messages.append(m)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly while trying to create a message with valid content and associated with a user")

    def test_message_associations(self):
        """Test if messages are properly associated with a User model"""
        # Associations:
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

        m = Message(text="Hello World")

        u.messages.append(m)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        # Can a message be successfully associated with a user (i.e., does the user_id foreign key work as expected)?
        self.assertEqual(
            m.user_id, u.id, "Messages are not seccessfully associated with a user (i.e., does the user_id foreign key does not work as expected)")

        # Can you retrieve the user associated with a given message?
        self.assertEqual(u, User.query.get(m.user_id),
                         "Cannot retrieve a user associated with a given message")

    def test_message_timestamp(self):
        """Test if message timestamps are functioning properly"""
        # Timestamps:
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

        m = Message(text="Hello World")

        u.messages.append(m)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        # Does the timestamp property of a message get set automatically upon creation?
        self.assertNotEqual(
            m.timestamp, None, "The timestamp property of a message is failing to set automatically upon creation")
        self.assertNotEqual(
            m.timestamp, "", "The timestamp property of a message is failing to set automatically upon creation")

    def test_message_likes(self):
        """Test if messages likes are functioning properly"""
        # Likes:
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

        msg = Message(text="New Message")
        u1.messages.append(msg)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when u1 tried creating a message")

        # Can a user like a message?
        new_like = Likes(user_id=u2.id, message_id=msg.id)
        db.session.add(new_like)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when u2 tried to like a message posted by u1")

        # Can a user unlike a message?
        Likes.query.filter(and_(Likes.user_id == u2.id,
                           Likes.message_id == msg.id)).delete()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when u2 tried to remove a like on a post")

    def test_message_deletion(self):
        """Test if message deletion is functioning"""
        # Deletion:
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

        msg = Message(text="New Message")
        msg2 = Message(text="New Message 2")
        u1.messages.append(msg)
        u2.messages.append(msg2)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when u1 tried creating a message")

        new_like = Likes(user_id=u2.id, message_id=msg.id)
        db.session.add(new_like)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(f"db.session.commit() raised {type(e)} unexpectedly!")

        # Can a message be successfully deleted from the database?
        db.session.delete(msg)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when trying to delete a message.")

        # When a message is deleted, are associated likes also removed (i.e., is the cascade delete working)?
        self.assertNotIn(new_like, Likes.query.all(
        ), "When a message is deleted, associated likes are not being removed (i.e., the cascade delete is not working).")

        # When a user is deleted, are all their messages also removed (i.e., is the cascade delete working)?
        db.session.delete(u2)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.fail(
                f"db.session.commit() raised {type(e)} unexpectedly when trying to delete a user.")

        self.assertNotIn(msg2, Message.query.all(
        ), "When a user is deleted, associated messages are not being removed (i.e., the cascade delete is not working).")

    def test_message_validations_and_constraints(self):
        """Test if message validations and constraints are functioning"""
        # Validations and Constraints:
        u = User.signup(
            username="testuser",
            password="PASSWORD",
            email="test@test.com",
            image_url=User.image_url.default.arg,
        )

        # Does the Message model prevent creation of a message without an associated user?
        db.session.add(Message(text="Hello World"))
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()
