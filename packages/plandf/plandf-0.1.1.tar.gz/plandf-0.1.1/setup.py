from setuptools import setup

setup(name='plandf',
    version='0.1.1',
    description='Pandas DataFrame for computing Value-Over-Time for lists of tuples (Step.investables, Step.deliverables) of a Plan.',
    url='https://github.com/WeFindX/PlanDF',
    author='Mindey I.',
    author_email='desk@infty.xyz',
    license='MIT',
    packages=['plandf'],
    install_requires=[
        'stepio>=0.1',
        'pandas>=0.17.1',
    ],
    extras_require = {
        'conversion_rates':  ["fred==3.1",
                              "requests>=2.9.1"],
    },
    zip_safe=False)
