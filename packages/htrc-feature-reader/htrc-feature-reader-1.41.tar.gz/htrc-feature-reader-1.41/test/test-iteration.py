from htrc_features import FeatureReader
import glob
import time

paths = glob.glob('data/*.json.bz2')
fr = FeatureReader(paths)
vol = fr.next()
vol = fr.next()
pages = vol.pages()
for i in range(15):
    page = pages.next()
print(page.tokenlist.token_counts())


