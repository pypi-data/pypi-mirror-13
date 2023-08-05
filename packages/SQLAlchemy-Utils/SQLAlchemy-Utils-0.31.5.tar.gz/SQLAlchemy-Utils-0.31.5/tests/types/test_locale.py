import sqlalchemy as sa
from pytest import mark, raises

from sqlalchemy_utils.types import locale
from tests import TestCase


@mark.skipif('locale.babel is None')
class TestLocaleType(TestCase):
    def create_models(self):
        class User(self.Base):
            __tablename__ = 'user'
            id = sa.Column(sa.Integer, primary_key=True)
            locale = sa.Column(locale.LocaleType)

            def __repr__(self):
                return 'User(%r)' % self.id

        self.User = User

    def test_parameter_processing(self):
        user = self.User(
            locale=locale.babel.Locale(u'fi')
        )

        self.session.add(user)
        self.session.commit()

        user = self.session.query(self.User).first()

    def test_territory_parsing(self):
        ko_kr = locale.babel.Locale(u'ko', territory=u'KR')
        user = self.User(locale=ko_kr)
        self.session.add(user)
        self.session.commit()

        assert self.session.query(self.User.locale).first()[0] == ko_kr

    def test_coerce_territory_parsing(self):
        user = self.User()
        user.locale = 'ko_KR'
        assert user.locale == locale.babel.Locale(u'ko', territory=u'KR')

    def test_scalar_attributes_get_coerced_to_objects(self):
        user = self.User(locale='en_US')

        assert isinstance(user.locale, locale.babel.Locale)

    def test_unknown_locale_throws_exception(self):
        with raises(locale.babel.UnknownLocaleError):
            self.User(locale=u'unknown')
