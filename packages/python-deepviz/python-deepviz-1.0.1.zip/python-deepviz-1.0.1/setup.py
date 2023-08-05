import setuptools

setuptools.setup(
        name='python-deepviz',
        version='1.0.1',
        author='Saferbytes',
        author_email='info@saferbytes.it',
        url='https://www.deepviz.com/',
        description='Deepviz Threat Intelligence API Client Library for python',
        keywords="deepviz API SDK",
        license='MIT',
        packages=['deepviz'],
        install_requires=[
            'requests>=2.5.1',
            'simplejson>=3.8.1'
        ]
)