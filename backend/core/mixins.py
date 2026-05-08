from django.db import models
from django.utils.text import slugify


class SystemObjectMixin(models.Model):
    is_system = models.BooleanField(default=False)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        abstract = True

    _slug_source_field = None

    def _get_slug_base(self):
        return slugify(getattr(self, self._slug_source_field))

    def _generate_unique_slug(self):
        base = self._get_slug_base()
        slug = base
        n = 2
        while type(self).objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                stored_slug = type(self).objects.values_list("slug", flat=True).get(pk=self.pk)
                self.slug = stored_slug
            except type(self).DoesNotExist:
                pass
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)
