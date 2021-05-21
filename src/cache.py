import time


class CachedObject:
    def __init__(self, name, value):
        self.name = str(name)
        self.value = value
        # timestamp in seconds
        self.time_created = time.time()


class Cache:
    def __init__(self, max_amount_of_objects = 5, seconds_before_deletion = 900):
        self.cached_objects = {}
        self.max_amount_of_objects = max_amount_of_objects
        self.seconds_before_deletion = seconds_before_deletion


    def add(self, item_to_cache: CachedObject):
        self.cached_objects[item_to_cache.name] = item_to_cache.value
        self.refresh()


    def refresh(self):
        """
        delete items when either there are more than [max_amount_of_object] items or the item is more than [seconds_before_deletion] seconds old
        """
        # if too many items in cache, delete the least-recently added
        if len(self.cached_objects.keys()) > self.max_amount_of_objects:
            del self.cached_objects[next(iter(self.cached_objects))]

        # if item added more than 5 minutes ago, delete
        for object_name in self.cached_objects.keys():
            if self.cached_objects[object_name].time_created - time.time() > self.seconds_before_deletion:
                del self.cached_objects[object_name]

