from setuptools import setup, find_packages

setup(
    name='EmployeeFaceSystem',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'opencv-python',
        'openpyxl',
        'APScheduler'
    ],
    entry_points={
        'console_scripts': [
            'employeefacesystem=app:main'
        ]
    }
)
