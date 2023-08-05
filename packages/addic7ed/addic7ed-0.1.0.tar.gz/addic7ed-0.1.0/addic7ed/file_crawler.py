import os
import re

from termcolor import colored

from addic7ed.serie_process import pre_process

REGEX = r"(.*)\.[s|S]?([0-9]{1,2})[x|X|e|E]?([0-9]{2})\..*([0-9]+p)?.*"


class FileCrawler:
    def __init__(self):
        self.episodes = {}
        for f in os.listdir():
            if f.endswith((".avi", "mkv", ".mp4")):
                ep = self._parse_filename(f)
                if ep:
                    self.episodes[f] = ep

    def _parse_filename(self, filename):
        m = re.match(REGEX, filename)
        if m:
            return Episode(
                filename,
                pre_process(m.group(1).replace('.', '_').lower()),
                int(m.group(2)),
                int(m.group(3))
            )
        else:
            return None


class Episode:
    def __init__(self, f, serie, season, episode):
        self.infos = {
            "serie": serie,
            "season": season,
            "episode": episode,
        }
        self.filename, self.extension = os.path.splitext(f)
        m = re.search(r"-(.*)%s$" % self.extension, f)
        self.infos["group"] = m.group(1) if m else ""

    def rename(self, new_name):
        try:
            os.rename("%s%s" % (self.filename, self.extension),
                      "%s%s" % (new_name, self.extension))
            print(colored("Renamed %s to %s" % (self.filename, new_name),
                          "green"))
            self.filename = new_name
        except Exception as e:
            print(e)
