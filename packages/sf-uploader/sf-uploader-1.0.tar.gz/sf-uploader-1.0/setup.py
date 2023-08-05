"""
starflyer - upload
==================

Upload module for starflyer which allows for users to upload files and optionally process them. 

"""
from setuptools import setup


setup(
    name='sf-uploader',
    version='1.0',
    url='',
    license='BSD',
    author='Christian Scholz',
    author_email='cs@comlounge.net',
    description='Upload module for starflyer',
    long_description=__doc__,
    packages=['sfext',
              'sfext.uploader',
             ],
    namespace_packages=['sfext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'starflyer',
        'PIL',
    ],
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
    ,
    entry_points="""
          [console_scripts]
          reprocess = sfext.uploader.scripts.reprocess:reprocess
    """,
)
