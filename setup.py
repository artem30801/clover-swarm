import setuptools

extras = {
    "lint": ["black", "flake8", "isort"],
}

setuptools.setup(
    name="clover_swarm",
    author="Artem Vasiunik",
    packages=setuptools.find_packages(),
    extras_require=extras,
    python_requires=">=3.6",
)
