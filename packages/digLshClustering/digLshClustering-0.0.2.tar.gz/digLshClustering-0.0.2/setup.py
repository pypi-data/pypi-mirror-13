try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


config = {
    'name': 'digLshClustering',
    'description': 'code to cluster based on lsh algorithm',
    'author': 'Dipsy Kapoor',
    'url': 'https://github.com/usc-isi-i2/dig-lsh-clustering.git',
    'download_url': 'https://github.com/usc-isi-i2/dig-lsh-clustering.git',
    'author_email': 'dipsykapoor@gmail.com',
    'install_requires': ['nose2',
                         'digSparkUtil',
                         'jq'],
    'version':'0.0.2',
    'packages': ['hasher', 'hasher.old', 'hasher.lsh','gen_int_input','clusterer','clusterer.old','utils'],
    'scripts': []
}

setup(**config)
