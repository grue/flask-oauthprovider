from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class ResourceOwner(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    request_tokens = relationship("RequestToken", order_by="RequestToken.id", backref="resource_owner")
    access_tokens = relationship("AccessToken", order_by="AccessToken.id", backref="resource_owner")

    def __init__(self, username, password):
        self.username = username
        # TODO: scrypt, flask login?
        self.password = password

    def __repr__(self):
        return "<User (%s)>" % (self.username,)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_key = Column(String)
    name = Column(String)
    description = Column(String)
    secret = Column(String)
    pubkey = Column(String)

    request_tokens = relationship("RequestToken", order_by="RequestToken.id", backref="client")
    access_tokens = relationship("AccessToken", order_by="AccessToken.id", backref="client")
    callbacks = relationship("Callback", order_by="Callback.id", backref="client")

    def __init__(self, client_key, name, description, secret=None, pubkey=None):
        self.client_key = client_key
        self.name = name
        self.description = description
        self.secret = secret
        self.pubkey = pubkey

    def __repr__(self):
        return "<Client (%s, %s)>" % (self.name, self.id)


class Callback(Base):
    __tablename__ = "callbacks"

    id = Column(Integer, primary_key=True)
    callback = Column(String)

    client_id = Column(Integer, ForeignKey("clients.id"))
    #client = relationship("Client", backref=backref("callbacks", order_by=id))

    def __init__(self, callback):
        self.callback = callback

    def __repr__(self):
        return "<Callback (%s, %s)>" % (self.callback, self.client)


class Nonce(Base):
    __tablename__ = "nonces"

    id = Column(Integer, primary_key=True)
    nonce = Column(String)
    timestamp = Column(Integer)

    # TODO: TTL
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", backref=backref("nonces", order_by=id))

    request_token_id = Column(Integer, ForeignKey("requestTokens.id"))
    request_token = relationship("RequestToken", backref=backref("nonces", order_by=id))

    access_token_id = Column(Integer, ForeignKey("accessTokens.id"))
    access_token = relationship("AccessToken", backref=backref("nonces", order_by=id))

    def __init__(self, nonce, timestamp):
        self.nonce = nonce
        self.timestamp = timestamp

    def __repr__(self):
        return "<Nonce (%s, %s, %s, %s)>" % (self.nonce, self.timestamp, self.client, self.resource_owner)


class RequestToken(Base):
    __tablename__ = "requestTokens"

    id = Column(Integer, primary_key=True)
    token = Column(String)
    verifier = Column(String)
    realm = Column(String)
    secret = Column(String)
    callback = Column(String)

    # TODO: TTL
    client_id = Column(Integer, ForeignKey("clients.id"))
    clients = relationship("Client", backref=backref("requestTokens", order_by=id))

    resource_owner_id = Column(Integer, ForeignKey("users.id"))
    resource_owners = relationship("ResourceOwner", backref=backref("requestTokens", order_by=id))

    def __init__(self, token, callback, secret=None, verifier=None, realm=None):
        self.token = token
        self.secret = secret
        self.verifier = verifier
        self.realm = realm
        self.callback = callback

    def __repr__(self):
        return "<RequestToken (%s, %s, %s)>" % (self.token, self.client, self.resource_owner)


class AccessToken(Base):
    __tablename__ = "accessTokens"

    id = Column(Integer, primary_key=True)
    token = Column(String)
    realm = Column(String)
    secret = Column(String)

    # TODO: TTL
    client_id = Column(Integer, ForeignKey("clients.id"))
    clients = relationship("Client", backref=backref("accessTokens", order_by=id))

    resource_owner_id = Column(Integer, ForeignKey("users.id"))
    resource_owners = relationship("ResourceOwner", backref=backref("accessTokens", order_by=id))

    def __init__(self, token, secret=None, verifier=None, realm=None):
        self.token = token
        self.secret = secret
        self.verifier = verifier
        self.realm = realm

    def __repr__(self):
        return "<AccessToken (%s, %s, %s)>" % (self.token, self.client, self.resource_owner)
