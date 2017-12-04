import urlparse
import os

SQLALCHEMY_TRACK_MODIFICATIONS = False

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])
database=url.path[1:],
user=url.username,
password=url.password,
host=url.hostname,
port=url.port

SQLALCHEMY_DATABASE_URI = "postgresql://" + user + ":" + password + "@" + host + ":" + port + "/" + database
