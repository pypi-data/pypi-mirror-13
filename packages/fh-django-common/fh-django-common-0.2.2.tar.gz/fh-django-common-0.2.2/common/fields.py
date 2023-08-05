from django.db.models.fields import FloatField


class OrdinalField(FloatField):

    def __init__(self, *args, **kwargs):
        kwargs['null'] = kwargs.get('null', False)
        kwargs['default'] = kwargs.get('default', 0)
        super(OrdinalField, self).__init__(*args, **kwargs)