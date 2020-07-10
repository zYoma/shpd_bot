from config import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<User %r>' % self.user_hash


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Contact, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Contact %r>' % self.date
