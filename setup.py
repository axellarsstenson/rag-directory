from setuptools import setup, find_packages

setup(
    name="rag-directory",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "sentence-transformers>=2.2.0",
        "rich>=13.0.0",
        "requests>=2.28.0",
        "PyPDF2>=3.0.0",
        "markdown>=3.4.0",
        "html2text>=2020.1.16",
        "scikit-learn>=1.0.0",
        "numpy>=1.21.0",
    ],
    entry_points={
        "console_scripts": [
            "rag-directory=rag_directory.cli:main",
        ],
    },
    author="Axel Stenson",
    author_email="axellarsstenson@gmail.com",
    description="A RAG tool for local directories using Ollama models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/axellarsstenson/rag-directory",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
)