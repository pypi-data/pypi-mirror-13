from setuptools import setup

version = '0.2'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'setuptools',
    'zest.releaser',
    ],

tests_require = [
    'coverage',
    'mock',
    'nose',
    ]

setup(name='qgispluginreleaser',
      version=version,
      description="Add-on for zest.releaser for releasing qgis plugins",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='https://github.com/nens/qgispluginreleaser',
      license='GPL',
      packages=['qgispluginreleaser'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ],
          'zest.releaser.releaser.after_checkout': [
              'release_plugin = qgispluginreleaser.entry_point:create_zipfile',
          ],
          'zest.releaser.prereleaser.middle': [
              'prerelease_plugin = qgispluginreleaser.entry_point:fix_version',
          ],
          'zest.releaser.postreleaser.middle': [
              'postrelease_plugin = qgispluginreleaser.entry_point:fix_version',
          ],
      })
