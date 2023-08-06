from setuptools import setup

setup(name='twittermetrics',
      version='0.1.5',
      description='Twitter search for popular words and sentiment analysis',
      url='https://github.com/dennokorir/project-mining-twitter.git',
      author='Denis Korir',
      author_email='dennokorir@gmail.com',
      license='MIT',
      packages=['twittermetrics'],
      install_requires=[
          'twitter','prettytable','requests'
      ],
      zip_safe=False)

