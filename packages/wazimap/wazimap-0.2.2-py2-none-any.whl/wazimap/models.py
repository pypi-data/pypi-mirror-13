from collections import OrderedDict
import itertools

from django.db import models
from django.utils.text import slugify


# Geographies
class GeoMixin(object):
    def as_dict(self):
        return {
            'full_geoid': self.geoid,
            'full_name': self.full_name,  # profile views use this as a name
            'name': self.full_name,  # API views use this as a name
            'short_name': self.name,
            'geo_level': self.geo_level,
            'geo_code': self.geo_code,
            'child_level': self.child_level,
            'parent_geoid': self.parent_geoid,
            'square_kms': self.square_kms,
        }

    def as_dict_deep(self):
        return {
            'this': self.as_dict(),
            'parents': OrderedDict((p.geo_level, p.as_dict()) for p in self.ancestors()),
        }

    def children(self):
        """ Get all objects that are direct children of this object.
        """
        return self.__class__.objects\
            .filter(parent_level=self.geo_level,
                    parent_code=self.geo_code)\
            .all()

    def split_into(self, level):
        """ Walk down the level hierarchy from here and return
        all the objects that are of geo_level +level+ and descendents
        of this geography.
        """
        candidates = self.children()
        while candidates:
            kids = set(c for c in candidates if c.geo_level == level)
            if kids:
                return list(kids)
            candidates = list(itertools.chain(c.children() for c in candidates))
        return []

    @property
    def full_name(self):
        if hasattr(self, 'long_name'):
            return self.long_name

        names = [self.name]
        names += [a.name for a in self.ancestors()]
        return ', '.join(names)

    @property
    def geoid(self):
        return '-'.join([self.geo_level, self.geo_code])

    @property
    def parent_geoid(self):
        if self.parent_level and self.parent_code:
            return '%s-%s' % (self.parent_level, self.parent_code)
        return None

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def child_level(self):
        # official child level
        from wazimap.geo import geo_data
        kids = geo_data.geo_levels[self.geo_level]['children']
        return kids[0] if kids else None

    def __unicode__(self):
        return self.full_name


class Geography(models.Model, GeoMixin):
    geo_level = models.CharField(max_length=15, null=False)
    geo_code = models.CharField(max_length=10, null=False)

    name = models.CharField(max_length=20, null=False, db_index=True)
    year = models.IntegerField(db_index=True, null=True)
    # this place's id from Open Street Map (OSM), useful when using
    # OSM for geolocation
    osm_area_id = models.IntegerField(db_index=True, null=True)

    # area in square km
    square_kms = models.FloatField(null=True)

    # hierarchy
    parent_level = models.CharField(max_length=15, null=True)
    parent_code = models.CharField(max_length=10, null=True)

    class Meta:
        unique_together = ('geo_level', 'geo_code')

    @property
    def parent(self):
        if not hasattr(self, '_parent'):
            if self.parent_level and self.parent_code:
                self._parent = self.__class__.objects.filter(geo_level=self.parent_level, geo_code=self.parent_code).first()
            else:
                self._parent = None

        return self._parent

    def ancestors(self):
        ancestors = []
        g = self.parent
        while g:
            ancestors.append(g)
            g = g.parent
        return ancestors
