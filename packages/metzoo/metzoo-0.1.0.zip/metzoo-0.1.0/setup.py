from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='metzoo',
      version='0.1.0',
      description='Python SDK for Metzoo',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='metzoo monitoring metric',
      url='https://bitbucket.org/edrans/metzoo-sdk/python',
      author='Edrans',
      author_email='info@edrans.com',
      license='MIT',
      packages=['metzoo'],
      install_requires=['requests'],
      zip_safe=False)