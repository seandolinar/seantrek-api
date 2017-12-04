import os
import urlparse


SQLALCHEMY_TRACK_MODIFICATIONS = False

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])
database=url.path[2:]
user=url.username
password=url.password
host=url.hostname
port=url.port





SQLALCHEMY_DATABASE_URI = "postgresql://" + str(user) + ":" + str(password) + "@" + str(host) + ":" + str(port) + "/" + str(database)
