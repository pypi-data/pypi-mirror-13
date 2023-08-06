from setuptools import setup, find_packages

version = '5.0.0'

setup(
    name='Products.SimpleAttachment',
    version=version,
    description="Simple Attachments for Plone",
    long_description=(open("README.rst").read() + '\n' +
                      open('CHANGES.rst').read()),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Plone attachments RichDocument',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://github.com/collective/Products.SimpleAttachment',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'archetypes.schemaextender',
        'plone.app.blob',
    ],
    extras_require={'test': [
        'zope.testing',
        'collective.testcaselayer',
        'Products.PloneTestCase',
        'Products.RichDocument',
    ]},
)
