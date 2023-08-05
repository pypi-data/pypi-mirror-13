import setuptools

setuptools.setup(
        name='python-deepviz',
        version='1.0.0',
        author='Saferbytes s.r.l.s.',
        author_email='info@saferbytes.it',
        url='https://www.deepviz.com/',
        description='Deepviz API Client Library for python',
        keywords="deepviz API SDK",
        license='MIT',
        packages=['deepviz'],
        install_requires=[
            'requests>=2.5.1',
            'simplejson>=3.8.1'
        ]
)
