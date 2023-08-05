from setuptools import setup


setup(
    name="hello_pylab_example",
    version="0.0.1",
    description="Simplesmente Hi",
    url="http://github.com/seuprojeto/hello",
    author="Seu Nome",
    author_email="seu@email.com",
    license="GPL",
    packages=["hello"],
    test_suite="nose.collector",
    tests_require=["nose"],
    zip_safe=False
)
