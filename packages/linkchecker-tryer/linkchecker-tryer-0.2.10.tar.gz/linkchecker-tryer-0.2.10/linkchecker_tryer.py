import re, sys, time, os
import fileinput
from subprocess import call, STDOUT


def parse_linkchecker_output(linkchecker_output):
    pattern = re.compile(r"^URL\s+\`(?P<url>.*?)\'$\n" +
                         r"(^Name\s+\`(?P<name>.*?)\'$\n)?" +
                         r"^Parent URL\s+(?P<parent>.*?)$\n"+
                         r".*^Result\s+(?P<result>.*?)$"
                         , flags=re.M + re.S)
    de_quote = re.compile(r"\`(.*)\'")

    def read_one(block):
        return {
                "url":block.group("url"),
                "name":block.group("name"),
                "parent_url":block.group("parent"),
                "message":de_quote.sub(r'\1', block.group(0))}

    return {str(x.group("url")):read_one(x) for x in pattern.finditer(linkchecker_output)}.values()


def bad_link(link):
    with open(os.devnull, 'w') as FNULL:
        return call(["linkchecker", "-r0", link["url"]], stdout=FNULL, stderr=STDOUT) != 0


def filter_out_good_links(links, filter_function):
    if links: time.sleep(30)
    return filter(filter_function, links)


def main():
    result = reduce(
            filter_out_good_links,
            [bad_link] * 3,
            parse_linkchecker_output(
                ''.join(fileinput.input())))
    print("\n")
    print("-------------------------------------------------")
    print("----------=========FINAL RESULT========----------")
    print("-------------------------------------------------")
    for r in result:
        print(r["message"])
        print
    if result: sys.exit(1)
