from setuptools import setup, find_packages
from dashmat import VERSION

setup(
      name = "dashmat"
    , version = VERSION
    , packages = find_packages(exclude=['tests'])
    , include_package_data = True

    , install_requires =
      [ "docker-harpoon==0.6.6.8"

      , "six"
      , "redis"
      , "croniter"
      , "requests"
      , "slumber"

      , "Flask==0.10.1"
      , "tornado==4.3"
      , "pyjade==3.1.0"
      , "pyYaml==3.10"
      ]

    , extras_require =
      { "tests":
        [ "noseOfYeti>=1.5.0"
        , "nose"
        , "mock==1.0.1"
        , "tox"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'dashmat = dashmat.executor:main'
        ]
      }

    # metadata for upload to PyPI
    , url = "https://github.com/realestate-com-au/dashmat"
    , author = "Stephen Moore"
    , author_email = "stephen.moore@rea-group.com"
    , description = "Application that reads yaml and serves up a pretty dashboard"
    , license = "MIT"
    , keywords = "dashboard"
    )

