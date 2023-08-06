from django.db.models import *
from django.utils.timezone import now


class SharkModel(Model):
    class Meta:
        abstract = True

    def __iter__(self):
        for field_name in self._meta.get_fields():
            yield field_name

    @classmethod
    def load(cls, id):
        return cls.objects.get(id=id)


class EditableText(SharkModel):
    name = CharField(max_length=128, primary_key=True, unique=True)
    filename = CharField(max_length=1024)
    handler_name = CharField(max_length=512)
    line_nr = IntegerField()
    last_used = DateTimeField(default=now())