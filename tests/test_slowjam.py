import time

from slowjam.trace import jam
from slowjam.context import slowjam_context
from slowjam.statsd_client import graphite_count


def test_slowjam():
    slowjam_context.start('my_application', extras={'testing': True})

    with jam('wait', extras={'delay': 3}):
        time.sleep(3)

        with jam('wait.itererate', extras={'iterations': 1000}):
            b = []
            for i in xrange(0, 1000):
                b += [i]

        graphite_count('wait.iterate.finished')

    profile = slowjam_context.stop()
    profile_dump = profile.to_dict()

    assert profile_dump['event'] == 'my_application'
    assert 'testing' in profile_dump['extras']
    assert profile_dump['extras']['testing'] == True
    assert profile_dump['is_marker'] == False
    assert 'start_time' in profile_dump
    assert 'stop_time' in profile_dump
    assert profile_dump['start_time'] > 1
    assert profile_dump['stop_time'] > 1
    assert len(profile_dump['inner_events']) == 1
    assert len(profile_dump['inner_events'][0]['inner_events']) == 2
    assert profile_dump['inner_events'][0]['inner_events'][1]['is_marker'] == True
