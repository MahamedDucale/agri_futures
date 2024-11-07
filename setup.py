from setuptools import setup, find_packages

setup(
    name="agri_futures",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.23",
        "psycopg2-binary>=2.9.1",
        "python-dotenv>=0.19.0",
        "stellar-sdk>=8.1.0",
        "twilio>=7.11.0",
        "requests>=2.26.0",
        "python-multipart>=0.0.5",
        "pydantic>=1.8.2",
        "aiohttp>=3.8.0",
        "pytest>=6.2.5",
        "alembic>=1.7.1",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A micro-futures platform for rural farmers using SMS, Stellar blockchain, and mobile money",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agri_futures",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "agri-futures=src.api.routes:app",
        ],
    },
) 