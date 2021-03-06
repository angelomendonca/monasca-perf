from urlparse import urlparse
from threading import Thread
import httplib, sys, multiprocessing
from Queue import Queue
import simplejson
import time

#Run as "time python perfprocess.py > out 2>&1 &" then "tail -f out"

num_processes = int(sys.argv[1])
num_threads = int(sys.argv[2])
num_requests = int(sys.argv[3])
num_metrics_per_request = int(sys.argv[4])

print num_processes * num_threads * num_requests * num_metrics_per_request

headers = {"Content-type": "application/json", "X-Auth-Token": "2685f55a60324c2ca6b5b4407d52f39a"}

urls = [
    'http://localhost:8080/v2.0/metrics',
]

def doWork(q):
    url=q.get()
    for x in xrange(num_requests):
        status,response=getStatus(url)
        doSomethingWithResult(status,response)
    q.task_done()

def getStatus(ourl):
    try:
        url = urlparse(ourl)
        conn = httplib.HTTPConnection(url.netloc)
        body = []
        for i in xrange(num_metrics_per_request):
            epoch = (int)(time.time()) - 120
            body.append({"name": "test-" + str(i), "dimensions": {"dim-1": "value-1"}, "timestamp": epoch, "value": i})
        body = simplejson.dumps(body)
        conn.request("POST", url.path, body, headers)
        res = conn.getresponse()
        if res.status != 204:
            raise Exception(res.status)
        return res.status, ourl
    except Exception as ex:
        print ex
        return "error", ourl

def doSomethingWithResult(status, url):
    pass

def doProcess():
    q=Queue(num_threads)
    for i in range(num_threads):
        t=Thread(target=doWork, args=(q,))
        t.daemon=True
        t.start()
    try:
        for i in xrange(num_threads):
            url = urls[i%len(urls)]
            q.put(url.strip())
        q.join()
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    jobs = []
    for i in range(num_processes):
        p = multiprocessing.Process(target=doProcess)
        jobs.append(p)
        p.start()
        p.join()

