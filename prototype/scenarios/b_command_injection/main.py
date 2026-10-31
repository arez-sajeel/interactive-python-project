import sys

from reports import generate_report


def main(argv):
    name = argv[1] if len(argv) > 1 else "monthly"
    generate_report(name)


if __name__ == "__main__":
    main(sys.argv)
