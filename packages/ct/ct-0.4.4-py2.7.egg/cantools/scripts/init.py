import os
from optparse import OptionParser
from cantools import config
from cantools.util import log, cp, sym, mkdir

HOME = os.environ.get("HOME", ".")

class Builder(object):
	def __init__(self, pname=None, cantools_path=HOME, web_backend="dez", refresh_symlinks=False):
		if not pname and not refresh_symlinks:
			pname = raw_input("project name? ")
		log("Initializing %s Project: %s"%(web_backend, pname or "(whatever)"))
		self.pname = pname
		self.cantools_path = cantools_path
		self.web_backend = web_backend
		if not refresh_symlinks:
			self.build_dirs()
			self.make_files()
		self.generate_symlinks(refresh_symlinks)
		log("done! goodbye.", 1)

	def build_dirs(self):
		log("building directories", 1)
		mkdir(self.pname)
		os.chdir(self.pname)
		mkdir("js")
		mkdir("html")

	def make_files(self):
		log("generating configuration", 1)
		cp((self.web_backend == "gae") and "%s\r\n%s"%(config.init.yaml.gae,
			config.init.yaml.core)%(self.pname,) or config.init.yaml.core, "app.yaml")
		cp(config.init.ctcfg%(self.web_backend,), "ct.cfg")
		log("demo index page", 1)
		cp(config.init.html%(self.pname,), os.path.join("html", "index.html"))

	def generate_symlinks(self, refresh=False):
		log("creating symlinks", 1)
		if refresh and not os.path.isdir("js"):
			mkdir("js")
		ctroot = os.path.join(self.cantools_path, "cantools", "cantools")
		if self.web_backend == "gae":
			sym(ctroot, "cantools")
		sym(os.path.join(ctroot, "CT"), os.path.join("js", "CT"))
		sym(os.path.join(ctroot, "css", "ct.css"), os.path.join("html", "ct.css"))

def parse_and_make():
	parser = OptionParser("ctinit [projname] [--cantools_path=PATH] [--web_backend=BACKEND]")
	parser.add_option("-c", "--cantools_path", dest="cantools_path", default=HOME,
		help="where is cantools? (default: %s)"%(HOME,))
	parser.add_option("-w", "--web_backend", dest="web_backend", default="dez",
		help="web backend. options: dez, gae. (default: dez)")
	parser.add_option("-r", "--refresh_symlinks", action="store_true",
		dest="refresh_symlinks", default=False, help="add symlinks to project")
	options, args = parser.parse_args()
	Builder(len(args) and args[0], options.cantools_path,
		options.web_backend, options.refresh_symlinks)

if __name__ == "__main__":
	parse_and_make()