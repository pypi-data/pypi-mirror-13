from setuptools import setup


with open('README.rst', 'r') as fh:
    description = '\n'.join(fh.readlines())

tests_require = [
    'pytest>=2.6.0',
    'pytest-cov>=1.7.0',
]

setup(
    name='django-ci-emailfield',
    version='0.0.1',
    description=description,
    url='https://github.com/mvantellingen/django-ciemailfield',
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    install_requires=[],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    package_dir={'': 'src'},
    py_modules=['django_ciemailfield'],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
)
