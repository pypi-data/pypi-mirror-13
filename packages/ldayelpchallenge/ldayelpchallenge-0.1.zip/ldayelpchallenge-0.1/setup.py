from setuptools import setup

setup(name='ldayelpchallenge',
      version='0.1',
      description='Run Latent Dirichlet Allocation on the reviews provided by Yelp for the Yelp data challenge',
      url='https://github.com/koschr/ldaforyelpchallenge',
      download_url='https://github.com/koschr/ldaforyelpchallenge/tarball/1.0',
      author='CK',
      author_email='test@example.com',
      license='MIT',
      packages=['ldayelpchallenge'],
      install_requires=['gensim', 'numpy', 'nltk', 'stop_words', 'langdetect'],
      zip_safe=False)