"""
Account model
"""
from datetime import date
from service import db


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class Account(db.Model):
    """Class that represents an Account"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(256))
    phone_number = db.Column(db.String(32))
    date_joined = db.Column(db.Date, nullable=False, default=date.today)

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes an Account into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone_number": self.phone_number,
            "date_joined": self.date_joined.isoformat(),
        }

    def deserialize(self, data):
        """Sets attributes from a dictionary"""
        try:
            self.name = data["name"]
            self.email = data["email"]
            self.address = data.get("address")
            self.phone_number = data.get("phone_number")
            if data.get("date_joined"):
                self.date_joined = date.fromisoformat(data["date_joined"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid Account: missing " + error.args[0]
            ) from error
        except (TypeError, ValueError) as error:
            raise DataValidationError(
                "Invalid Account: bad or missing data"
            ) from error
        return self

    def create(self):
        """Creates an Account in the database"""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Updates an Account in the database"""
        db.session.commit()

    def delete(self):
        """Removes an Account from the database"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def all(cls):
        """Returns all Accounts"""
        return cls.query.all()

    @classmethod
    def find(cls, account_id):
        """Finds an Account by its id"""
        return db.session.get(cls, account_id)
