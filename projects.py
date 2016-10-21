import requests
from auth import GitHubCredentials, ensure_cred
import logging


logger = logging.getLogger("projects")
_BASE_URL = "https://api.github.com/"


class HTTPRequest(object):
	def __init__(self):
		self.creds = None
		self.headers = {
			"Accept": "application/vnd.github.inertia-preview+json",
			"Authorization": None
		}

	def _check_creds(self):
		if not self.creds:
			self.creds = GitHubCredentials(username, password)
			self.headers["Authorization"] = "Basic {}".format(self.creds.b64_auth())

	@ensure_cred
	def get(self, url):
		return request.get(url)

	@ensure_cred
	def post(self, url):
		return request.get(url)


class Project(object):
	def __init__(self, owner, repo):
		self.owner = owner
		self.repo = repo
		self.cred = None
		self.name = None
		self.id = None
		self._number = None
		self._proj_url = "{url}repos/{owner}/{repo}/projects".format(
			url=_BASE_URL, 
			owner=self.owner, 
			repo=self.repo,
		)

		self.request = HTTPRequest()

	def create(self, name, desc, username, password):
		url = self._proj_url
		data = dict(
			name=name,
			body=desc
		)

		return requests.post(url, json=data, headers=self.headers)

	def list_projects(self):
		response = requests.get(self._proj_url)
		return response.json()

	def get_project(self, proj_number=None):
		if not proj_number:
			proj_number = self.number

		url = self._proj_url + "/{number}".format(number=proj_number)
		response = requests.get(url)
		return response.json()

	@property
	def number(self):
		return self._number

	@number.setter
	def number(self, n):
		self._number = n


class Column(object):
	def __init__(self, name):
		self.id = None
		self.name = name
		self.project_url = None
		self.created_at = None
		self.updated_at = None


class ProjectBoard():
	def __init__(self, project):
		"""
		Default template for QED team project boards
		"""
		self.project = project
		self.user_stories = Column("User Stories")
		self.new = Column("New")
		self.in_progress = Column("In Progress")
		self.ready_for_test = Column("Ready for Testing")
		self.closed = Column("Closed")
		
		self.default_cols = [
			self.user_stories,
			self.new,
			self.in_progress,
			self.ready_for_test,
			self.closed
		]
		

	def list_cols(self):
		url = self._proj_url + "/{number}".format(number=proj_number)
		response = requests.get(url)
		return response.json()

	def create_default_cols(self):
		url = self._proj_url + "/{number}/columns".format(number=proj_number)

		for col in self.default_cols:
			data = dict(name=col.name)
			response = self.request.post(url, json=data)
			if response.code == 201:
				pass
			else:
				raise Error("Error: {code}\n{content}".format(code=response.code, content=response.content))

		logger.info("Successfully created {n} columns!".format(n=len(self.default_cols)))