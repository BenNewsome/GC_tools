"""
Downloads the test dataset from atsmosviz as the files are too large for gitgub.
"""

def get_all_files():
    """
    Downloads all the test dataset files using rsync.
    """
    import os
    if not os.path.isfile("test_files/ctm.nc"):
        os.system("""(cd test_files && wget -r -nH -nd -np -R --no-parent --reject "index.html*" http://atmosviz1.york.ac.uk/~bn506/data/GC_funcs_test/test_files/)""")

    return

if __name__=='__main__':
    get_all_files()



