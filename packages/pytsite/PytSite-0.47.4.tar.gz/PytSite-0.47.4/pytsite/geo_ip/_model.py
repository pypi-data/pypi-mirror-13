"""GeoIP Package ODM Models.
"""
from decimal import Decimal as _Decimal
from pytsite import odm as _odm, geo as _geo

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class GeoIP(_odm.Model):
    @property
    def ip(self) -> str:
        return self.f_get('ip')

    @property
    def asn(self) -> str:
        return self.f_get('asn')

    @property
    def city(self) -> str:
        return self.f_get('city')

    @property
    def country(self) -> str:
        return self.f_get('country')

    @property
    def country_code(self) -> str:
        return self.f_get('country_code')

    @property
    def isp(self) -> str:
        return self.f_get('isp')

    @property
    def latitude(self) -> _Decimal:
        return self.f_get('latitude')

    @property
    def longitude(self) -> _Decimal:
        return self.f_get('longitude')

    @property
    def lng_lat(self) -> list:
        return self.f_get('lng_lat')

    def organization(self) -> str:
        return self.f_get('organization')

    @property
    def postal_code(self) -> int:
        return self.f_get('postal_code')

    @property
    def region(self) -> str:
        return self.f_get('region')

    @property
    def region_name(self) -> str:
        return self.f_get('region_name')

    @property
    def timezone(self) -> str:
        return self.f_get('timezone')

    def _setup(self):
        """Hook.
        """
        self.define_field(_odm.field.String('ip', nonempty=True))
        self.define_field(_odm.field.String('asn'))
        self.define_field(_odm.field.String('city'))
        self.define_field(_odm.field.String('country'))
        self.define_field(_odm.field.String('country_code'))
        self.define_field(_odm.field.String('isp'))
        self.define_field(_odm.field.Decimal('latitude'))
        self.define_field(_odm.field.Decimal('longitude'))
        self.define_field(_geo.field.LngLat('lng_lat'))
        self.define_field(_odm.field.String('organization'))
        self.define_field(_odm.field.String('postal_code'))
        self.define_field(_odm.field.String('region'))
        self.define_field(_odm.field.String('region_name'))
        self.define_field(_odm.field.String('timezone'))

        self.define_index(('ip', _odm.I_ASC), unique=True)
        self.define_index(('lng_lat', _odm.I_GEO2D))

    def _on_f_set(self, field_name: str, value, **kwargs):
        """Hook.
        """
        if field_name == 'longitude':
            self.f_set('lng_lat', [value, self.latitude])

        if field_name == 'latitude':
            self.f_set('lng_lat', [self.longitude, value])

        return value
