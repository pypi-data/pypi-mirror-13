from setuptools import setup

setup(name='messageconnoisseur',
      version='0.2.0',
      description='Message log parser and message processor',
      url='http://github.com/spasticVerbalizer/messageconnoisseur',
      author='Maarten van den Berg',
      author_email='schoenveter123+git@gmail.com',
      license='MIT',
      packages=['messageconnoisseur'],
      zip_safe=False,
      entry_points = {
          'console_scripts': [
              'mc-import-file=messageconnoisseur.scripts:import_file_script',
              'mc-import-dir=messageconnoisseur.scripts:import_directory_script',
              'mc-leaderboard=messageconnoisseur.scripts:leaderboard_all_time_script',
              'mc-fortune=messageconnoisseur.scripts:random_quote_script',
              ]
          }
)
