from setuptools import setup  # , find_packages

setup(name='basespaceapp',
      version='0.0.3',
      description='template for basespace native app.',
      url='https://github.com/alaindomissy/basespaceapp',
      author='Alain Domissy',
      author_email='alaindomissy@gmail.com',
      license='MIT',
      # packages=find_packages(exclude=["tests"]),
      packages=['basespaceapp'],
      install_requires=[
            'six'
      ],
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
      ],
      zip_safe=False)
