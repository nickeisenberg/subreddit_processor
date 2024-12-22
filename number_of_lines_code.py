import os
lines = 0
for root, dir, files in os.walk("/home/nicholas/gitrepos/ticker_sentiment"):
    for f in files:
        fpath = os.path.join(root, f)
        if fpath.endswith(".pyc"):
            continue
        if ".git" in fpath:
            continue
        if fpath.endswith(".txt"):
            continue
        if fpath.endswith(".csv"):
            continue
        try:
            with open(fpath, "r") as ff:
               lines += len(ff.readlines())
        except:
            print(os.path.join(root, f))
print(lines)

