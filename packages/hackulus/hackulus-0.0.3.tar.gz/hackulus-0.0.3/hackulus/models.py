import mongoengine as mongo
from mongoengine import fields

class Hacker(mongo.Document):
    uid = fields.StringField()
    username = fields.StringField()
    email = fields.EmailField()