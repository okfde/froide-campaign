import os

from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            full_path = self.path(name)
            os.remove(full_path)
        return name
