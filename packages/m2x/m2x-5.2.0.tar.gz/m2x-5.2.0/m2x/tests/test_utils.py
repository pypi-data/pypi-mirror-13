from datetime import datetime

from iso8601 import iso8601

from m2x import utils


class TestUtils(object):
    def test_to_utc(self):
        dtime = datetime.now()
        utc_dtime = utils.to_utc(dtime)
        assert isinstance(utc_dtime.tzinfo, iso8601.Utc)

    def test_to_iso(self):
        dtime = iso8601.parse_date('2015-04-15 12:00:00+0300')
        iso_time = utils.to_iso(dtime)
        assert iso_time == '2015-04-15T15:00:00.000000Z'
        dtime = '2015-04-15 12:00:00'
        iso_time = utils.to_iso(dtime)
        assert iso_time == '2015-04-15T15:00:00.000000Z'

    def test_tags_to_server(self):
        tags = utils.tags_to_server(['foo', 'bar'])
        assert tags == 'foo,bar'
        tags = utils.tags_to_server(['foo'])
        assert tags == 'foo'
        tags = utils.tags_to_server('foo')
        assert tags == 'foo'
        tags = utils.tags_to_server(None)
        assert tags == ''
        tags = utils.tags_to_server([None])
        assert tags == ''
        tags = utils.tags_to_server([''])
        assert tags == ''

    def test_from_server(self):
        out = utils.from_server('tags', 'foo,bar')
        assert out == ['foo', 'bar']
        out = utils.from_server('timestamp', '2015-04-15T15:00:00.000000Z')
        assert out.year == 2015 and out.month == 4 and out.day == 15
        assert out.hour == 15 and out.minute == 0 and out.second == 0
        assert isinstance(out.tzinfo, iso8601.Utc)
        out = utils.from_server('ignored', 'just a string')
        assert out == 'just a string'
        out = utils.from_server('ignored', 123)
        assert out == 123

    def test_to_server(self):
        out = utils.to_server('tags', ['foo', 'bar'])
        assert out == 'foo,bar'
        dtime = iso8601.parse_date('2015-04-15 12:00:00+0300')
        out = utils.to_server('timestamp', dtime)
        assert out == '2015-04-15T15:00:00.000000Z'
        out = utils.to_server('ignored', 'just a string')
        assert out == 'just a string'
        out = utils.to_server('ignored', 123)
        assert out == 123

    def test_attrs_from_server(self):
        values = {'tags': 'foo,bar',
                  'timestamp': '2015-04-15 12:00:00+0300',
                  'ignored1': 'just a string',
                  'ignored2': 123}
        out = utils.attrs_from_server(values)
        assert out['tags'] == ['foo', 'bar']
        assert out['timestamp'] == iso8601.parse_date(
            '2015-04-15 12:00:00+0300'
        )
        assert out['ignored1'] == 'just a string'
        assert out['ignored2'] == 123

    def test_attrs_to_server(self):
        values = {'tags': ['foo', 'bar'],
                  'timestamp': iso8601.parse_date('2015-04-15 12:00:00+0300'),
                  'ignored1': 'just a string',
                  'ignored2': 123}
        out = utils.attrs_to_server(values)
        assert out['tags'] == 'foo,bar'
        assert out['timestamp'] == '2015-04-15T15:00:00.000000Z'
        assert out['ignored1'] == 'just a string'
        assert out['ignored2'] == 123
