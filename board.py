


class Column(object):
	def __init__(self, name):
		self.id = None
		self.name = name
		self.project_url = None
		self.created_at = None
		self.updated_at = None


class ProjectBoard(object):
	def __init__(self, project):
		self.project = project

	def create_cols(self, cols):
		url = self.project._proj_url + "/{number}/columns".format(number=self.project.number)

		for col in cols:
			data = dict(name=col.name)
			response = self.project.request.post(url, json=data)
			if response.status_code == 201:
				pass
			else:
				print("Return code = {code} at:{url}".format(
					code=response.status_code,
					url=url
				))


class QedSprintBoard(ProjectBoard):
	def __init__(self, project):
		"""
		Default template for QED team project boards
		"""
		super(QedSprintBoard, self).__init__(project)
		self.user_stories = Column("User Stories")
		self.new = Column("New")
		self.in_progress = Column("In Progress")
		self.ready_for_test = Column("Ready for Testing")
		self.closed = Column("Closed")
		
		self.cols = [
			self.user_stories,
			self.new,
			self.in_progress,
			self.ready_for_test,
			self.closed
		]
