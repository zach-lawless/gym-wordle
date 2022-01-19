from setuptools import setup

setup(name='gym_wordle',
      version='0.0.1',
      install_requires=['gym==0.17.2',
                        'numpy>=1.19.2'],
      package_data={'gym_wordle': ['data/*.txt']}
)
