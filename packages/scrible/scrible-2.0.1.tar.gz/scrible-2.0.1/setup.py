from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='scrible',
      version='2.0.1',
      long_description=readme(),
      description='Note taking application',
      url='https://github.com/jaxtreme01/Scrible',
      author='Jack Mwangi',
      author_email='jackmwa94@gmail.com',
      keywords='notes taking app scrible scribbler scribble',
      license='MIT',
      entry_points={
          'console_scripts': ['scrible = scrible.notes.scrible:main'],
      },
      download_url = 'https://github.com/jaxtreme01/Scrible/tarball/0.2.1',
      packages=['scrible'],
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=['docopt', 'clint', 'requests', 'python-firebase'
                        'colorama','pyfiglet','termcolor'],
      include_package_data=True,
      zip_safe=False)

