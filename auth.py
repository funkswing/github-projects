import base64


class GitHubCredentials(object):
	def __init__(self, username, password):
		self.user_pass = "{u}:{p}".format(u=username, p=password)

	def b64_auth(self):
		return base64.b64encode(self.user_pass)


def ensure_cred(f):
	def decorator(*args, **kwargs):

		print("Checking creds....")

		return f(*args, **kwargs)
	return decorator