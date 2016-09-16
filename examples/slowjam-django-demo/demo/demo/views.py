from django.http import HttpResponse
import requests
import requests.packages.urllib3
from slowjam.trace import span, annotate

requests.packages.urllib3.disable_warnings()


def demo_view(request):
    delay = request.GET.get('delay', 1)

    with span('demo_view.request1', extras={'delay': delay}):
        resp = requests.get('https://httpbin.org/delay/{}'.format(delay))

    with span('demo_view.request2', extras={'delay': delay}):
        resp = requests.get('https://httpbin.org/delay/{}'.format(delay))

    with span('demo_view.request3', extras={'delay': delay}):
        resp = requests.get('https://httpbin.org/delay/{}'.format(delay))

    annotate('demo_view.requests', extras={'total_time': delay * 3})

    return HttpResponse('This is a nice view <br><pre>{}</pre>'.format(resp.content))
