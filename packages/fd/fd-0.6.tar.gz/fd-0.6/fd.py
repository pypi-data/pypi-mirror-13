'''
Copyright (c) 2015, John Emmons
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import filelock
import getopt
import pickledb
import os
import shutil
import sys
import sqlite3

CONFIG_FILE = 'config.json'
FILE_NUM_VAR = 'num_files'

METADATA_DB_NAME = 'metadata.sqlite3'
TABLE_NAME = 'files'
FILE_ID_COL_NAME = 'fid'
FILE_NAME_COL_NAME = 'name'

DATA_STORAGE_DIR_NAME = 'data'

LOCKS_DIR_NAME = 'locks'
DB_FILELOCK_NAME = 'db.lock'

def init(db_path, force=False):
    try:
        os.stat(db_path)
        
        if(not force):
            print "Directory or database already exists. Use -f or --force to delete and initialize"
            return
        else:
            shutil.rmtree(db_path)
    except:
        pass

    os.mkdir(db_path)
    os.mkdir( os.path.join(db_path, DATA_STORAGE_DIR_NAME) )
    os.mkdir( os.path.join(db_path, LOCKS_DIR_NAME) )
    
    conn = sqlite3.connect( os.path.join(db_path, METADATA_DB_NAME) )
    c = conn.cursor()
    c.execute('CREATE TABLE %s(%s INT, %s TEXT)' % (TABLE_NAME, FILE_ID_COL_NAME, FILE_NAME_COL_NAME))
    conn.close()

    config = pickledb.load( os.path.join(db_path, CONFIG_FILE), True) 
    config.set(FILE_NUM_VAR, 0)
    config.dump()
        
def ls(db_path):
    lock = filelock.FileLock( os.path.join(db_path, LOCKS_DIR_NAME, DB_FILELOCK_NAME) )
    with lock:
        conn = sqlite3.connect( os.path.join(db_path, METADATA_DB_NAME) )
        c = conn.cursor()

        for row in c.execute('SELECT %s FROM %s' % (FILE_NAME_COL_NAME, TABLE_NAME)):
            print row
                
def put(db_path, file_name, tags=None):
    lock = filelock.FileLock( os.path.join(db_path, LOCKS_DIR_NAME, DB_FILELOCK_NAME) )
    with lock:
        config = pickledb.load( os.path.join(db_path, CONFIG_FILE), True) 
        file_num = config.get(FILE_NUM_VAR)
        
        conn = sqlite3.connect( os.path.join(db_path, METADATA_DB_NAME) )
        c = conn.cursor()
        
        try:
            shutil.move(file_name, os.path.join(db_path, DATA_STORAGE_DIR_NAME, str(file_num)) )
        except IOError:
            print "Insertion error: file not found"
            exit(0)
        except:
            print 'Insertion error!'
            exit(0)

        c.execute('INSERT INTO %s (fid, name) VALUES (?, ?)' % TABLE_NAME, (file_num, file_name))
        conn.commit()
        conn.close()
            
        config.set(FILE_NUM_VAR, file_num+1)
        config.dump()
        print tags

def get():
    lock = filelock.FileLock( os.path.join(db_path, LOCKS_DIR_NAME, DB_FILELOCK_NAME) )
    with lock:
        pass

def rm():
    lock = filelock.FileLock( os.path.join(db_path, LOCKS_DIR_NAME, DB_FILELOCK_NAME) )
    with lock:
        pass

