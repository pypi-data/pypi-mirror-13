from setuptools import setup, find_packages

setup(
  name = 'crowdrouter',
  packages = find_packages(exclude=['example', 'dist', 'build']),
  version = '1.5.3',
  description = 'A framework for architecting tasks to the crowd.',
  long_description = "The CrowdRouter is a framework for creating crowdsourcing workflows and tasks in web applications.",
  license = "MIT",
  author = 'Mario Barrenechea',
  author_email = 'mbarrenecheajr@gmail.com',
  install_requires = ["pickledb"],
  url = 'https://github.com/Project-EPIC/crowdrouter', # use the URL to the github repo
  download_url = 'https://github.com/Project-EPIC/crowdrouter/archive/1.5.3.tar.gz',
  keywords = ['crowdsourcing', 'tasks', 'workflows'], # arbitrary keywords
  classifiers = [],
)
