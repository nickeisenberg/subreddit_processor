import os
lines = 0
for root, dir, files in os.walk("/home/nicholas/gitrepos/ticker_sentiment"):
    for f in files:
        fpath = os.path.join(root, f)
        if not fpath.endswith(".py"):
            continue
        try:
            with open(fpath, "r") as ff:
               lines += len(ff.readlines())
        except:
            print(os.path.join(root, f))
print(lines)
