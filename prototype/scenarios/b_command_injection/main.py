import sys
from reports import generate_report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <report_name>")
        sys.exit(1)

    generate_report(sys.argv[1])
