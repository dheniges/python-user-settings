import os
from pathlib import Path
from abc import ABC, abstractmethod

import aiofiles
import aiofiles.os

# Choose a parent directory for the FileStorage class's settings to be stored.
# Default to application directory
# Settings will be put in a subdirectory named 'user-settings'
FILE_STORAGE_SETTINGS_DIR = './'

# An abstract class defining the interface to be implemented for other storage solutions
#
# We could get fancier and utilize some dynamic features of Python to validate
# the implementations of our BaseStorage class using a metaclass and issubclass()
class BaseStorage(ABC):
    @abstractmethod
    async def read(self, key: str) -> str | bool:
        pass

    @abstractmethod
    async def write(self, key: str, body: str) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

# Cache layer in front of all storage implementations.
# Stores values in a dict in memory.
# Naive implementation with no TTL or max cache size.
# Could run out of memory if service spammed with new user settings
class StorageCache(BaseStorage):
    def __init__(self, storageKlass: BaseStorage):
        self.storage = storageKlass()
        # We could pre-warm the cache here if desired
        self.cache = {}

    async def read(self, key):
        val = self.cache.get(key)
        if val:
            return val
        else:
            val = await self.storage.read(key)
            if val:
                self.cache[key] = val
                return val
        return False
    
    async def write(self, key, body):
        result = await self.storage.write(key, body)
        if result:
            self.cache[key] = body
            return True
        return False
    
    async def delete(self, key):
        result = await self.storage.delete(key)
        if result:
            if key in self.cache:
                del self.cache[key]
            return True
        return False

# The default FileStorage class
# Utilizes aiofiles for async file I/O
class FileStorage(BaseStorage):
    USER_SETTINGS_DIR = 'user-settings'
    SETTINGS_FILE_PATH = os.path.join(FILE_STORAGE_SETTINGS_DIR, USER_SETTINGS_DIR)

    def __init__(self):
        try:
            Path(self.SETTINGS_FILE_PATH).mkdir(parents=True, exist_ok=True)
        except Exception:
            raise PermissionError(f'Unable to write to directory {self.SETTINGS_FILE_PATH}. Change permissions or update FILE_STORAGE_SETTINGS_DIR to a writeable directory')

    async def read(self, key):
        full_path = os.path.join(self.SETTINGS_FILE_PATH, key)
        if await aiofiles.os.path.isfile(full_path) == False:
            return False
        
        try:
            async with aiofiles.open(full_path, 'r') as file:
                content = await file.read()
                return content
        except Exception:
            return False
    
    async def write(self, key, body):
        full_path = os.path.join(self.SETTINGS_FILE_PATH, key)

        try:
            async with aiofiles.open(full_path, 'w') as file_handler:
                await file_handler.write(body)
            return True
        except Exception as e:
            print(e)
            return False
    
    async def delete(self, key):
        full_path = os.path.join(self.SETTINGS_FILE_PATH, key)
        if await aiofiles.os.path.isfile(full_path) == False:
            return False
        try:
            await aiofiles.os.unlink(full_path)
            return True
        except Exception:
            return False

# Default storage implementation. To swap implementations,
# pass a new class that implements the BaseStorage abstract class
# to StorageCache
storageInstance = StorageCache(FileStorage)