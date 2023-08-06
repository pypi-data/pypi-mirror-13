from setuptools import setup, find_packages

setup(name='cs1110grade',
      version='0.0',
      description='Tools for automated grading of cs1110 assignments.',
      url='https://github.com/fredcallaway/grade.py',
      author='Fred Callaway',
      author_email='fredc@llaway.com',
      license='MIT',
      packages=['gradepy'],  
      scripts=['bin/grade.py'],
      include_package_data=True,
      zip_safe=False)