import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().strip().split("/n")

setuptools.setup(
    name="gamgee",
    version="0.3.0",
    author="Austin Poor",
    author_email="45295232+a-poor@users.noreply.github.com",
    description="Gamgee helps you get up and running quickly with an AWS Lambda API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a-poor/gamgee",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
)

