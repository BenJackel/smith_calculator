from setuptools import setup, find_packages

setup(
    name="smith_calculator",
    version="0.0.1",
    packages=find_packages(
        include=[
            "calculators",
            "calculators.*",
            "investment_calculator",
            "mortgage_calculator",
            "smith_calculator",
            "investment_calculator.*",
            "mortgage_calculator.*",
            "smith_calculator.*",
        ]
    ),
    tests_requires=["pytest"],
    install_requires=["pandas>=1.2.4", "streamlit>=0.86.0"],
)
