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
    'version':'0.0.4',
    'packages': ['digLshClustering.hasher','digLshClustering.hasher.lsh',
                 'digLshClustering.gen_int_input',
                 'digLshClustering.clusterer','digLshClustering.utils'],
    'scripts': []
}

setup(**config)
