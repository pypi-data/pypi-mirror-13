import distutils.core

version = '0.1'

distutils.core.setup(
        name='ctec_consumer',
        version=version,
        packages=['ctec_consumer'],
        author='ZhangZhaoyuan',
        author_email='zhangzhy@chinatelecom.cn',
        url='http://www.189.cn',
        description='189 rabbitMQ consumer'
)
