from setuptools import setup, find_packages

setup(
    name = 'weixincli',
    version = '0.0.1',
    keywords = ('weixin', 'wechat'),
    description = 'Weixin client in terminal.',
    license = 'GPL',
    install_requires = ['urwid>=1.3.1', 'qrcode>=5.2.2'],

    author = 'mtunique',
    author_email = 'oatgnem@gmail.com',

    packages = find_packages(),
    platforms = 'any',
)
