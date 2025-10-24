"""nfops-planner CLI"""
import argparse

def main():
    ap = argparse.ArgumentParser(prog="nfops-planner", description="NFOPS planner CLI")
    ap.add_argument("--version", action="store_true", help="show version")
    args = ap.parse_args()
    if args.version:
        print("nfops-planner 0.0.0")

if __name__ == "__main__":
    main()
