from setuptools import setup
from twitched import VERSION


setup(name="twitched",
      version=VERSION,
      description="A Python library for quickly writing Twitch chat applications and custom chat bots.",
      author="Jeff Merver",
      author_email="jeff@merver.me",
      url="https://github.com/jeffmvr/twitched",
      packages=[
          'twitched',
      ],
      keywords=[
          'irc',
          'twitch',
          'twitch.tv',
          'twitch chat',
          'twitch irc',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: No Input/Output (Daemon)',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Communications :: Chat',
          'Topic :: Games/Entertainment',
          'Topic :: Internet',
          'Topic :: Software Development',
      ],
)
