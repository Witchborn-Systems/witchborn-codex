from setuptools import setup, find_packages

setup(
    name="codexai",
    version="1.0.0",
    description="Official Client for the Witchborn Codex Protocol (ai://)",
    author="Witchborn Systems",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "cxlookup=codexai.cxlookup:main",     # The Admin Tool
            "codex-handle=codexai.handler:main",  # The OS Handler
        ],
    },
)