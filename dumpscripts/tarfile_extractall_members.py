# tarfile_extractall_members.py

import tarfile
import os

os.mkdir('outdir')
with tarfile.open('esempio.tar', 'r') as t:
    def is_within_directory(directory, target):
<<<<<<< HEAD

        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)

        prefix = os.path.commonprefix([abs_directory, abs_target])

        return prefix == abs_directory

    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):

=======
        
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
    
        prefix = os.path.commonprefix([abs_directory, abs_target])
        
        return prefix == abs_directory
    
    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
    
>>>>>>> a6fce59acd33d1c158af01831a7cc5aae14caf21
        for member in tar.getmembers():
            member_path = os.path.join(path, member.name)
            if not is_within_directory(path, member_path):
                raise Exception("Attempted Path Traversal in Tar File")
<<<<<<< HEAD

        tar.extractall(path, members, numeric_owner=numeric_owner) 


=======
    
        tar.extractall(path, members, numeric_owner=numeric_owner) 
        
    
>>>>>>> a6fce59acd33d1c158af01831a7cc5aae14caf21
    safe_extract(t, "outdir", members=[t.getmember("LEGGIMI.txt")])
                 members=[t.getmember('LEGGIMI.txt')],
                 )

print(os.listdir('outdir'))

