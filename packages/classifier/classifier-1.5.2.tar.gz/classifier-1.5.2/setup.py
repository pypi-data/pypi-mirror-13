
from setuptools import setup

setup(name="classifier",
	version="1.5.2",
	description="Classify the files in your Downloads folder into suitable destinations.",
	url="http://github.com/bhrigu123/classifier",
	author="Bhrigu Srivastava",
	author_email="captain.bhrigu@gmail.com",
	license='MIT',
	packages=["classifier"],
	entry_points="""
    [console_scripts]
    classifier = classifier.classifier:main
    """,
	zip_safe=False)
