from distutils.core import setup
setup(name='popt',
      packages=['popt'],
      version='0.1',
      description='Tool for converting Robot Framework xml output to a human-readable log file',
      author='Janne Kohvakka',
      author_email='jkohvakk@gmail.com',
      url='https://github.com/jkohvakk/popt',
      download_url='https://github.com/jkohvakk/mypackage/tarball/0.1',
      keywords=['Robot Framework', 'log'],
      classifiers=[],
      entry_points={'console_scripts': ['popt=popt:read_arguments']})
