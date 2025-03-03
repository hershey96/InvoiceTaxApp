
from setuptools import setup, find_packages

setup(
    name="invoicetaxapp",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "tkcalendar>=1.6.1",
        "pdfplumber>=0.7.6",
        "pillow>=9.3.0",
    ],
    entry_points={
        'console_scripts': [
            'invoicetaxapp=invoicetaxapp.app:main',
        ],
    },
    author="YOUR NAME",
    author_email="your.email@example.com",
    description="Business invoice management and tax calculation application",
    keywords="invoice, tax, accounting, business",
    url="https://github.com/YOUR_USERNAME/InvoiceTaxApp",
    python_requires='>=3.7',
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
