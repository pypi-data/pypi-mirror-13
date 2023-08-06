from setuptools import setup, find_packages


install_requires = [
    'chainer',
    'numpy',
    'pymongo',
    'pyzmq',
    'tornado',
    'pypandoc',
    'pytz',
    'python-dateutil',
]


CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    "Topic :: Utilities",
    "License :: OSI Approved :: MIT License",
]

packages = [
    'room',
    'room.buffer',
    'room.database',
    'room.filter',
    'room.forwarder',
    'room.miner',
    'room.output',
    'room.parser',
    'room.publisher',
    'room.zmq_base',
]


# pypandocを使ってREADME.mdをrstに変換する。最初からrstで書いた場合は不要。
try:  
    import pypandoc
    read_md = lambda f: pypandoc.convert(f, 'rst')
except ImportError:  
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

dist = setup(  
        name='room',                        # パッケージ名
        version='0.1.8',                    # バージョン
        author='takatorino',                # 作者の名前
        author_email='tktr3w5e0@gmail.com', # 連絡先
        url='https://github.com/takatori',  # GitHubのリポジトリとか
        license='MIT',                      # ライセンス
        description="A framework of stream data maining for smart home",
        keywords='data mining, smart home, api',
        classifiers=CLASSIFIERS, # 詳細は http://pypi.python.org/pypi?:action=list_classifiers を参照
        packages=find_packages(exclude=['examples', 'tests']),
        include_package_data=True,
        zip_safe=False,
        install_requires=install_requires,     # インストールする依存パッケージ
)
