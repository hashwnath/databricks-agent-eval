from setuptools import setup, find_packages

setup(
    name="databricks-agent-eval",
    version="0.1.0",
    description="Multi-agent evaluation harness for supervisor-agent workflows",
    author="Hashwanth Sutharapu",
    author_email="hsuthara@asu.edu",
    url="https://github.com/hashwnath/databricks-agent-eval",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0.0",
        "langchain>=0.3.0",
        "langgraph>=0.2.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0", "pytest-asyncio>=0.23.0"],
    },
    entry_points={
        "console_scripts": [
            "agent-eval=eval.cli:main",
        ],
    },
)
