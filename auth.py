import base64


class GitHubCredentials(object):
	def __init__(self, username, password):
		user_pass = "{u}:{p}".format(u=username, p=password)

	def b64_auth(self):
		return base64.b64encode(user_pass)
