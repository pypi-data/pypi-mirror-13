from retask import Queue
queue = Queue('example')
queue.connect()
while queue.length != 0:
    task = queue.dequeue()
    print "We received: ", task.data
    queue.send(task, "We received your information dear %s" % task.data['user'])

