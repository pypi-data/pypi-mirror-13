from setuptools import setup

def readme():
    with open('README.rst') as f:
        return(f.read())

setup(name='pyoutube',
      version='0.2.1',
      description='Upload videos to youtube using OAuth2.0 and the youtube API',
      long_description=readme(),
      classifieres=['Development Status :: 1 - Alpha',
                    'Programming Language :: Python :: 3.4'],
      keywords='youtube upload uploader', 
      author='lpbrown999',
      author_email='lpbrown999@gmail.com',
      packages=['pyoutube'],
      install_requires = ['google-api-python-client'],
      zip_safe=False)