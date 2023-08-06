from setuptools import setup

setup(name='quetzalcoatl',
      version='0.1.3',
      description='An image processing and computer vision toolbox/library',
      url='http://github.com/colmex/quetzalcoatl',
      author='Luis Hernandez',
      author_email='luisfmh@gmail.com',
      license='MIT',
      packages=['quetzalcoatl'],
      install_requires=[
            "numpy",
      ],
      zip_safe=False)
