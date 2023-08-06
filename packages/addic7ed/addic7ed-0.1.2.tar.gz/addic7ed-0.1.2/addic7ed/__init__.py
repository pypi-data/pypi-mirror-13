from termcolor import colored

from .parser import Addic7edParser
from .file_crawler import FileCrawler

crawler = FileCrawler()
parser = Addic7edParser()


def addic7ed():
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print(colored("\nBye!", "yellow"))
        exit(0)


def main():
    for filename, ep in crawler.episodes.items():
        subs = parser.parse(**ep.infos)

        print(ep)

        if not subs:
            print(colored("No subtitles for %s" % filename, "red"),
                  end="\n\n")
            continue

        for i, sub in enumerate(subs):
            print("[%s] %s" % (colored(i, "yellow"), sub))

        version = input('Download number? ')

        if not version:
            print(colored("Nothing to do!", "yellow"),
                  end="\n\n")
            continue

        try:
            filename = subs[int(version)].download()
            print(colored("Downloaded %s subtitle file" % filename, "green"))
            if filename:
                print(ep.rename(filename),
                      end="\n\n")
        except Exception as e:
            print(colored(e, "red"),
                  end="\n\n")
