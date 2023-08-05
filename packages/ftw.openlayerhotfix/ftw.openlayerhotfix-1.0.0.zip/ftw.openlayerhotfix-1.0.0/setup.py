from setuptools import setup, find_packages

setup(
    name='ftw.openlayerhotfix',
    version='1.0.0',
    author='4teamwork AG',
    url='https://github.com/4teamwork/ftw.openlayerhotfix',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'collective.geo.openlayers <= 3.1',
        'Plone',
        'setuptools',
        'z3c.jbot',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
