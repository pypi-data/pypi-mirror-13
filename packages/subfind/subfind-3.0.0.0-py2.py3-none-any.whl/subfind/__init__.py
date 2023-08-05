import logging

import importlib
import os
import re
from abc import ABCMeta, abstractmethod
from os.path import join, exists, getsize
from subfind.utils.subtitle import subtitle_extensions
from .exception import MovieNotFound, SubtitleNotFound, ReleaseMissedLangError
from .movie_parser import parse_release_name
from .release.alice import ReleaseScoringAlice
from .scenario import ScenarioManager
from .utils import write_file_content

EVENT_SCAN_RELEASE = 'SCAN_RELEASE'
EVENT_RELEASE_FOUND_LANG = 'RELEASE_FOUND_LANG'
EVENT_RELEASE_COMPLETED = 'RELEASE_COMPLETED'
EVENT_RELEASE_MOVIE_NOT_FOUND = 'RELEASE_MOVIE_NOT_FOUND'
EVENT_RELEASE_SUBTITLE_NOT_FOUND = 'RELEASE_SUBTITLE_NOT_FOUND'


class BaseProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_sub_file(self, sub_page_url):
        """
        Get subtitle content of `sub_page_url`

        :param sub_page_url:
        :type sub_page_url:
        :return:
        :rtype: str
        """
        pass

    @abstractmethod
    def get_releases(self, release_name, langs):
        """
        Find all releases

        :param release_name:
        :type release_name:
        :param langs:
        :type langs:
        :return: A dictionary which key is lang, value is `release_info`
        :rtype:
        """
        return {}


class SubFind(object):
    def __init__(self, event_manager, languages, provider_names, force=False, min_movie_size=None):
        """

        :param event_manager:
        :type event_manager: subfind.event.EventManager
        :param languages:
        :type languages:
        :param provider_names:
        :type provider_names:
        :param force:
        :type force:
        :param min_movie_size:
        :type min_movie_size:
        :return:
        :rtype:
        """
        self.event_manager = event_manager
        self.force = force
        assert isinstance(languages, list) or isinstance(languages, set)

        if isinstance(languages, list):
            self.languages = set(languages)
        else:
            self.languages = languages

        self.movie_extensions = ['mp4', 'mkv']

        self.movie_file_pattern = re.compile('^(.+)\.\w+$')

        # Ignore movie file which size < min_movie_size
        self.min_movie_size = min_movie_size

        self.logger = logging.getLogger(self.__class__.__name__)

        scenario_map = {}
        for provider_name in provider_names:
            module_name = 'subfind_provider_%s' % provider_name
            module = importlib.import_module(module_name)
            class_name = '%sFactory' % provider_name.capitalize()
            clazz = getattr(module, class_name)
            data_provider = clazz()
            scenario_map[provider_name] = data_provider.get_scenario()

        self.scenario = ScenarioManager(ReleaseScoringAlice(), scenario_map)

    def scan(self, movie_dir):
        reqs = []
        for root_dir, child_folders, file_names in os.walk(movie_dir):
            # print root_dir, child_folders, file_names
            for file_name in file_names:
                for ext in self.movie_extensions:
                    if file_name.endswith('.%s' % ext):
                        if self.min_movie_size and getsize(join(root_dir, file_name)) < self.min_movie_size:
                            # Ignore small movie file
                            continue

                        save_dir = root_dir
                        m = self.movie_file_pattern.search(file_name)
                        if not m:
                            continue

                        release_name = m.group(1)

                        # Detect if the sub exists
                        if not self.force:
                            missed_langs = []
                            for lang in self.languages:
                                found = False
                                for subtitle_extension in subtitle_extensions:
                                    sub_file = join(root_dir, '%s.%s.%s' % (release_name, lang, subtitle_extension))
                                    if exists(sub_file):
                                        found = True
                                        break

                                if not found:
                                    missed_langs.append(lang)

                        if self.force:
                            reqs.append((release_name, save_dir, self.languages))
                        elif missed_langs:
                            reqs.append((release_name, save_dir, missed_langs))

        for release_name, save_dir, search_langs in reqs:
            try:
                subtitle_paths = []
                found_langs = set()
                self.event_manager.notify(EVENT_SCAN_RELEASE, (release_name, search_langs))

                for subtitle in self.scenario.execute(release_name, search_langs):
                    found_langs.add(subtitle.lang)

                    sub_file = '%s.%s.%s' % (release_name, subtitle.lang, subtitle.extension)
                    sub_file = join(save_dir, sub_file)
                    subtitle_paths.append(sub_file)
                    write_file_content(sub_file, subtitle.content)

                    self.event_manager.notify(EVENT_RELEASE_FOUND_LANG, (release_name, subtitle))

                self.event_manager.notify(EVENT_RELEASE_COMPLETED, {
                    'release_name': release_name,
                    'subtitle_paths': subtitle_paths,
                })
            except MovieNotFound as e:
                self.event_manager.notify(EVENT_RELEASE_MOVIE_NOT_FOUND, e)
            except SubtitleNotFound as e:
                self.event_manager.notify(EVENT_RELEASE_SUBTITLE_NOT_FOUND, e)
