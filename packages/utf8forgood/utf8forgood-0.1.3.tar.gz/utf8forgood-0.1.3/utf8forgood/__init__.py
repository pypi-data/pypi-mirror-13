# adopted from http://stackoverflow.com/questions/2276200/changing-default-encoding-of-python/17628350#17628350
# sys.setdefaultencoding() does not exist, here!
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
