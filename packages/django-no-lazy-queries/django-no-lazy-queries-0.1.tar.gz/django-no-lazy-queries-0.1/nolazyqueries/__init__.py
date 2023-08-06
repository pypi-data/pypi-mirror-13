import django
from contextlib2 import contextmanager
from mock import patch

if django.VERSION < (1, 9):
    from django.db.models.fields import related
    _lazy_descriptors = (
        related.SingleRelatedObjectDescriptor,
        related.ReverseSingleRelatedObjectDescriptor,
    )
else:
    from django.db.models.fields import related_descriptors
    _lazy_descriptors = (
        related_descriptors.ReverseOneToOneDescriptor,
        related_descriptors.ForwardManyToOneDescriptor,
    )


def _replacement_get(self, instance, owner):
    if instance is None:
        return self

    try:
        return getattr(instance, self.cache_name)
    except AttributeError:
        try:
            field_name = self.related.get_accessor_name()
        except AttributeError:
            field_name = self.field.name
        raise AttributeError('Cannot lazy load %s.%s, \
                use prefetch_related or select_related.' % (
            type(instance).__name__, field_name))


@contextmanager
def no_lazy_queries():
    '''
    Raise AttributeError instead of lazy loading related Django ORM models.

    NOT THREAD SAFE, for development only. This decorator temporarily breaks
    Django's lazy loading descriptors to raise a descriptive AttributeError
    instead of executing a potentially hard to find query.
    '''
    patches = []
    for descriptor in _lazy_descriptors:
        patch_obj = patch.object(descriptor, '__get__', new=_replacement_get)
        patch_obj.start()
        patches.append(patch_obj)

    try:
        yield
    finally:
        for patch_obj in patches:
            patch_obj.stop()
