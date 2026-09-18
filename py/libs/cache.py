class TaggedCache:
    """Compatibility facade which deliberately does not retain node outputs.

    ComfyUI owns model lifetime and offloading.  Keeping another strong reference
    here prevented ComfyUI from reclaiming models, even after its own cache had
    unloaded them.  Callers may keep using the old mapping API; a miss makes them
    load the resource for the current workflow execution instead.
    """

    def __init__(self, tag_settings=None):
        pass

    def __getitem__(self, key):
        raise KeyError(f'Key `{key}` does not exist')

    def __setitem__(self, key, value: tuple):
        return

    def __delitem__(self, key):
        raise KeyError(f'Key `{key}` does not exist')

    def __contains__(self, key):
        return False

    def items(self):
        return iter(())

    def get(self, key, default=None):
        """D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."""
        return default

    def clear(self):
        # clear all cache
        return

cache_settings = {}
cache = TaggedCache(cache_settings)
cache_count = {}

def update_cache(k, tag, v):
    # Intentionally do not retain models outside the node execution which loaded
    # them.  See TaggedCache's docstring.
    return
def remove_cache(key):
    if key == '*':
        cache.clear()
        cache_count.clear()
    elif key in cache:
        del cache[key]
        cache_count.pop(key, None)
    else:
        print(f"invalid {key}")
