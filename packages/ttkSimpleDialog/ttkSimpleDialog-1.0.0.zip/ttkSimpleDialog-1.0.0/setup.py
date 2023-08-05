from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["things/*"]

setup(name="ttkSimpleDialog",
      version="1.0.0",
      description="ttk themed version of ttkSimpleDialog",
      author="Tyler Holmes",
      author_email="tylerdanielholmes@gmail.com",
      url="holmesengineering.com",
      #Name the folder where your packages live:
      #(If you have other packages (dirs) or modules (py files) then
      #put them into the package directory - they will be found
      #recursively.)
      packages=['ttkSimpleDialog'],
      #'package' package must contain files (see list above)
      #I called the package 'package' thus cleverly confusing the whole issue...
      #This dict maps the package name== directories
      #It says, package *needs* these files.
      package_data={'ttkSimpleDialog': []},
      #'runner' is in the root.
      scripts=["runner"],
      long_description="""Identical to the tkSimpleDialog module, except the widgets used are ttk themed widgets.""",
      #
      #This next part it for the Cheese Shop, look a little down the page.
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'License :: Freely Distributable',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Topic :: Software Development :: User Interfaces',
      ]
      )
