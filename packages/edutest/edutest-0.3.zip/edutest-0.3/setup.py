from setuptools import setup

setup(
      name="edutest",
      version=0.3,
      description="Utility library for writing tests in the context of teaching programming",
      url="https://bitbucket.org/plas/edutest",
      license="MIT",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: Freeware",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Education",
        "Topic :: Software Development",
        "Topic :: Software Development :: Testing",
      ],
      keywords="testing",
      py_modules=["edutest",
                  "edutest_locale_et"]
)