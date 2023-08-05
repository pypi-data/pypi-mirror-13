from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='gitbit',
      version='0.1',
      description='Git automator written in bash and wrapped in python',
      url='http://github.com/anmolmahajan/git-bit',
      long_description=readme(),
      author='Anmol Mahajan',
      author_email='mahajan.anmol@gmail.com',
      license='MIT',
      packages=['git-bit'],
      scripts=['git-bit/gitbit','git-bit/gitting'],
      include_package_data=True,
      zip_safe=False)
