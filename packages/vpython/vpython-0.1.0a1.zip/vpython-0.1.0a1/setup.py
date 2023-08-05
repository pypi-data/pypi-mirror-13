from distutils.core import setup

setup(
    name='vpython',
    packages=['vpython'],
    version='0.1.0a1',
    description='VPython for Jupyter Notebook',
    long_description=open('README.txt').read(),
    author='Bruce Sherwood',
    author_email='bruce.sherwood@gmail.com',
    package_data={'vpython': ['data/*']},
    requires=['ipython'],
    url='http://testpypi.python.org/pypi/vpython/',
    license='LICENSE.txt',
    keywords='vpython',
    classifiers=[
          'Framework :: IPython',
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Graphics :: 3D Modeling',
          'Topic :: Multimedia :: Graphics :: 3D Rendering',
          'Topic :: Scientific/Engineering :: Visualization',
    ],
)