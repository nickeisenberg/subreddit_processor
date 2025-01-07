import os

def main():
    lines = 0
    for root, _, files in os.walk(os.getcwd()):
        for f in files:
            fpath = os.path.join(root, f)
            if not fpath.endswith(".py") or ".venv" in fpath:
                continue
            try:
                with open(fpath, "r") as ff:
                   lines += len(ff.readlines())
            except:
                print(os.path.join(root, f))
    print(lines)

if __name__ == "__main__":
    main()
