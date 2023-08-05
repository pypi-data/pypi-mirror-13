from distutils.core import setup

setup(
    author = 'Moroz Ilya',
    author_email = 'flamewowilia@gmail.com',
    description = 'Modification of PyAPNs python library for interacting with the Apple Push Notification Service',
    download_url = 'https://github.com/flamewow/PyAPNs.git',
    license = 'unlicense.org',
    name = 'apns3',
    py_modules = ['apns3'],
    scripts = ['apns-send'],
    url = 'https://github.com/flamewow/PyAPNs.git',
    version = '1.0.0',
)
