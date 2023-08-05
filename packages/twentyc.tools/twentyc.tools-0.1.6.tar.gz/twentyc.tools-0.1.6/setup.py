from setuptools import setup

version = open('config/VERSION').read().strip()
requirements = open('config/requirements.txt').read().split("\n")

setup(
    name='twentyc.tools',
    version=version,
    author='Twentieth Century',
    author_email='code@20c.com',
    description='various python tool libraries / helpers',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url='https://github.com/20c/twentyc.tools',
    download_url='https://github.com/20c/twentyc.tools/tarball/%s'%version,
    packages=['twentyc.tools'],
    install_requires=requirements,
    namespace_packages=['twentyc'],
    zip_safe=False
)
