from setuptools import setup

setup(
    name="django-social-network",
    #url = "http://github.com/dgarciavicente/django-notifications/",
    url="http://github.com/diana-gv/django-social-network/",
    author="Diana Garcia Vicente",
    author_email="dianagv@gmail.com",
    version="0.1.1",
    packages=["social_network", "social_network.templatetags", "social_network.migrations", "social_network.management",
              "social_network.management.commands"],
    include_package_data=True,
    zip_safe=False,
    description="Social Network for Django",
    install_requires=['django>=1.6.1', 'celery>=3.1.4', 'django-social-graph>=0.1.8', 'Django-Select2>=4.2.2',
                      'django-notifications'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Framework :: Django",
    ],

)
