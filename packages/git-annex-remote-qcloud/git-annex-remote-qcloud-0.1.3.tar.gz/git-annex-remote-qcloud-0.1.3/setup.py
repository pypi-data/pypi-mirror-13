from setuptools import setup

setup(name='git-annex-remote-qcloud',
      version='0.1.3',
      author='foreverbell',
      author_email='dql.foreverbell@gmail.com',
      url='https://github.com/foreverbell/git-annex-remote-qcloud',
      license='MIT',
      keywords='git-annex qcloud',
      description='git-annex external special remote protocol for qcloud (Tencent Cloud).',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7'
      ],
      packages=['git_annex_remote_qcloud'],
      install_requires=['requests'],
      entry_points={'console_scripts': ['git-annex-remote-qcloud = git_annex_remote_qcloud.main:main']})
