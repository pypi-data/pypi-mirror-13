from setuptools import setup, find_packages

setup(
    name = 'pytessert',
    version = '0.0.1',
    keywords = ('pytesser', 'pytesseract', 'pytessert'),
    description = "Python-tesseract is a python wrapper for google's Tesseract-OCR",
    license = 'MIT License',
    install_requires = ['tesseract>=3.03'],

    author = 'baituhuangyu',
    author_email = 'baituhuangyu@qq.com',
    
    packages = find_packages(),
    platforms = 'Ubuntu',
)
