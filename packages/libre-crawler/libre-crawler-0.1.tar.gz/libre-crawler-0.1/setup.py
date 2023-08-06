from setuptools import setup

setup(name='libre-crawler',
      version='0.1',
      description='Generic web crawler for stock photo websites',
      url='http://github.com/davegri/libre-crawler',
      author='David Griver',
      author_email='dgriver@gmail.com',
      license='MIT',
      packages=['librecrawler'],
      install_requires=[
          'requests',
          'beautifulsoup4',
      ],
      zip_safe=False)
