from setuptools import setup

setup(
      name="berkeley500A",
      description="API for Berkeley 500A delay generator",
      version="0.1.1",
      platforms=["any"],
      author="Markus J Schmidt",
      author_email='schmidt@ifd.mavt.ethz.ch',
      license="GNU GPLv3+",
      url="https://github.com/smiddy/berkeley500A",
      py_modules=["berkeley500A"],
      install_requires=['pyserial==2.7'],
      classifiers=[
                    'Development Status :: 4 - Beta',
                    'Intended Audience :: Science/Research',
                    'Topic :: Scientific/Engineering',
                    'License :: OSI Approved :: GNU General Public License v3 '
                    'or later (GPLv3+)',
                    'Programming Language :: Python :: 3.4',
                    ]
      )
