#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-film-noir.jarbasai=skill_film_noir:FilmNoirSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-film-noir',
    version='0.0.1',
    description='ovos classic scifi horror skill plugin',
    url='https://github.com/JarbasSkills/skill-film-noir',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_film_noir": ""},
    package_data={'skill_film_noir': ['locale/*', 'res/*']},
    packages=['skill_film_noir'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
