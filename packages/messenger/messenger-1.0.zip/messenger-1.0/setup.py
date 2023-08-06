from distutils.core import setup

setup(name='messenger',version="1.0",description="Connects 2 computers on the same network to pass text messages to each other",
author="Mark Ashton",author_email="baldydoc@gmail.com",py_modules=["messenger","messengerinterface"],url="http://www.baldydoc.com",
package_dir={"messenger":"messenger"})
