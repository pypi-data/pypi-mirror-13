from setuptools import setup, find_packages

setup(name='PAMMySQLTools',
      version_format='{tag}',
      version='0.0.1',
      description='A set of tools to manage users from pam_mysql',
      author='Christopher Perrin',
      author_email='perrin@uni-trier.de',
      url='https://gitlab.uni-trier.de/sad-team/PAMMySQL-Tools',
      license='MIT',
      packages=find_packages(),
      test_suite='tests',
      setup_requires=['setuptools-git-version'],
      install_requires=['pymysql', 'click'],
      entry_points={
          'console_scripts': [
              'myuseradd=pammymanager.scripts:useradd',
              'myuserdel=pammymanager.scripts:userdel',
              'myusermod=pammymanager.scripts:usermod',
              'mygroupadd=pammymanager.scripts:groupadd',
              'mygroupdel=pammymanager.scripts:groupdel',
              'mygroupmod=pammymanager.scripts:groupmod',
          ]
      },
      package_data= {
          'pammymanager': ['*.mo']
      },
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Environment :: Console"
      ])
