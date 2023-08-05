from setuptools import setup, find_packages


def requirements():
    """Build the requirements list for this project"""
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


setup(name='pikabu-telegram-bot',
      version='0.1.6',
      description='Pikabu bot for telegram. Powered by python-telegram-bot',
      author='Alexey Kalyaganov',
      author_email='admin@futurobot.ru',
      license='LGPLv3',
      include_package_data=True,
      packages=find_packages(exclude=['tests*']),
      install_requires=requirements(),
      )
