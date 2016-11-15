import requests
from auth import GitHubCredentials, ensure_cred
from board import ProjectBoard, QedSprintBoard, Column
import logging


logger = logging.getLogger("projects")
_BASE_URL = "https://api.github.com/"


class HTTPRequest(object):
	def __init__(self):
		self.headers = None
		self.creds = False

	def check_creds(self, username, password):
		creds = GitHubCredentials(username, password)
		self._set_headers(creds.b64_auth())

		response = requests.get(_BASE_URL, headers=self.headers)
		is_valid = self.is_valid(response.json())
		if is_valid:
			# GitHub API login successful!
			print("\n   Login Successful!\n")
			self.creds = True
			return True
		else:
			print("\n   Login Failed...\n")
			return False

	@staticmethod
	def is_valid(response_dict):
		if "message" in response_dict.keys():
			print("\n   {message}".format(message=response_dict["message"]))
			return False
		else:
			return True


	def _set_headers(self, b64_creds):
		"""
		GitHub API requires specific HTTPS headers:
			"Accept" - is a temporary custom content-type for the GitHub API preview period
			"Authorization" - for simplicity, we use Basic Auth, which is a Base64 transformation 
				of "user:passwd".
		"""
		self.headers = {
			"Accept": "application/vnd.github.inertia-preview+json",
			"Authorization": "Basic {}".format(b64_creds)
		}

	# @ensure_cred
	def get(self, url):
		return requests.get(url, headers=self.headers)

	# @ensure_cred
	def post(self, url, json):
		return requests.post(url, json=json, headers=self.headers)


class Project(object):
	def __init__(self, owner, repo, request=None):
		self.owner = owner
		self.repo = repo
		self.cred = None
		self.name = None
		self.id = None
		self._number = None
		self._BASE_URL = _BASE_URL
		self._proj_url = "{url}repos/{owner}/{repo}/projects".format(
			url=_BASE_URL, 
			owner=self.owner, 
			repo=self.repo,
		)
		self._proj_url_by_id = None
		self.request = request
		if not self.request:
			user, passwd = user_login()
			self.request = HTTPRequest(user, passwd)

	@property
	def number(self):
		return self._number

	@number.setter
	def number(self, n):
		self._number = n

	def create(self, name, desc):
		url = self._proj_url
		data = dict(
			name=name,
			body=desc
		)
		print(url)
		response = self.request.post(url, json=data)
		response_dict = response.json()

		# Set project "number" attribute
		self.number = response_dict["number"]
		# Set project "id" attribute
		self.id = response_dict["id"]
		# Now that we have the project id, set "_proj_url_by_id" property
		self._proj_url_by_id = "{url}projects/{id}/".format(
			url=self._BASE_URL, 
			id=self.id
		)

		return response.status_code

	def list_projects(self):
		response = self.request.get(self._proj_url)
		return response.json()

	def get_project(self, proj_number=None):
		if not proj_number:
			proj_number = self.number

		url = self._proj_url + "/{number}".format(number=proj_number)
		response = self.request.get(url)
		return response.json()

	def list_cols(self):
		url = self._proj_url + "/{number}".format(number=proj_number)
		response = self.request.get(url)
		return response.json()


def set_input():
	from sys import version_info
	
	py3 = version_info[0] > 2  # Check if using Python 3
	if py3:
		return input
	else:
		return raw_input


def user_login():
	from getpass import getpass
	input = set_input()

	user = input("Enter GitHub username (email address): ")
	passwd = getpass("Enter GitHub password (hidden): ")

	return user, passwd


def valid_repo(request, repo_name, repo_owner):

	repo_url = "{url}repos/{owner}/{repo}".format(
		url=_BASE_URL, 
		owner=repo_owner, 
		repo=repo_name,
	)
	response = request.get(repo_url)
	return request.is_valid(response.json())


def create_default_project_board(request):
	input = set_input()

	print("Enter GitHub repo and owner you wish to create a Sprint Board for...")
	repo_name = input("GitHub repo name: ")
	repo_owner = input("GitHub repo owner: ")

	if valid_repo(request, repo_name, repo_owner):
		proj = Project(repo_owner, repo_name, request)
	else:
		print("\n   Invalid GitHub repo referenced, try again...\n")
		create_default_project_board(request)
	
	proj_name = input("Project name: ")
	proj_desc = input("Project description: ")

	create_code = proj.create(proj_name, proj_desc)
	if create_code == 201:
		print("Project created successfully!")
	else:
		print("Return code = {code} at:{url}\nPlease try again.".format(
			code=response.status_code,
			url=url
		))
		return  # Error code, exit function...
	
	project_board = QedSprintBoard(proj)

	create_default_cols = input("Create default columns for {proj_name} project? (Y/N): ").format(
		proj_name=proj_name
	)
	if create_default_cols.lower() in ("y", "yes"):
		print("Creating default Sprint Board columns...")
		try:
			project_board.create_cols(project_board.cols)
			print("Default Sprint Board created!")
		except requests.exceptions.HTTPError as e:
			print("\n   {}\n".format(e))
			# clean_up(project_board)
		
	else:
		if create_default_cols.lower() not in ("n", "no"):
			print("Neither yes or no entered...assuming no...")
		print("Additional API funcationality coming soon...")


def main():
	user, passwd = user_login()
	request = HTTPRequest()
	request.check_creds(user, passwd)
	
	if request.creds:
		# Login successful!
		create_default_project_board(request)
	else:
		# Login failed, prompt user to re-enter GitHub login credentials
		main()


if __name__ == "__main__":
	main()
	