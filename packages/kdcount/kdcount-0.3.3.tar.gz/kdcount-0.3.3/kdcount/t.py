
def work(callback):
    for i in range(10):
        callback(i)

def callback(i):
    print i

def toiter(work):
    def cor():
        i = (yield)
        print 'yielding in coroutine', i
        yield i

    c = cor()
    print 'priming', c.next()

    def callback(i):
        if i == 0: c.send(None)
        print 'sending ', i
        c.send(i)
    work(callback)

    c.next()

    while True:
        print 'yielding'
        yield c.next()

#work(callback)
for i in toiter(work):
    print i
