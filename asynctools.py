import asyncio, requests, functools
import concurrent.futures


class AsyncTaskPoll:
    def __init__(self):
        self.tasks = []
    def queueup(self, task):
        self.tasks.append(task)
    def gather(self):
        return gather(self.tasks)

def get_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    finally:
        return loop

def executor(max_workers=None):
    return concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

def async_function(executor=None):
    def decorator(function):
        @functools.wraps(function)
        def async_call_wraper(*params, **optional_params):
            return call(function, *params, executor=executor, **optional_params)
        return async_call_wraper
    return decorator
# Most simple decorator:
make_asynchronous = async_function()

def call(function, *params, executor=None, **optional_params):
    loop = get_event_loop()
    return loop.run_in_executor(executor, functools.partial(function, *params, **optional_params))

def gather(tasks):
    loop = get_event_loop()
    return loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    import requests, time
    nb_inputs = 20
    inputs = [ v for v in range(nb_inputs) ]

    # First way:
    get = make_asynchronous(requests.get)
    async def square(a):
        response = await get("http://api.mathjs.org/v4/", params={'expr':"{}^2".format(a)})
        return int(response.text)

    T = time.time()
    response = gather([ square(v) for v in inputs ])
    T = time.time() - T
    print("First way, asynchronous get:")
    print("\tresults {} in {}s".format(response[:3]+["..."]+response[-3:], T))

    # Second way:
    @make_asynchronous
    def square_2(a):
        response = requests.get("http://api.mathjs.org/v4/", params={'expr':"{}^2".format(a)})
        return int(response.text)

    T = time.time()
    response = gather([ square_2(v) for v in inputs ])
    T = time.time() - T
    print("Second way, asynchronous square function:")
    print("\tresults {} in {}s".format(response[:3]+["..."]+response[-3:], T))

    # Third way fixed number of workers (here one per input):
    max_workers = nb_inputs
    with executor(max_workers) as exe:
        @async_function(exe)
        def square_2(a):
            response = requests.get("http://api.mathjs.org/v4/", params={'expr':"{}^2".format(a)})
            return int(response.text)

        T = time.time()
        response = gather([ square_2(v) for v in inputs ])
        T = time.time() - T
        print("Third way, asynchronous square function in a {}-workers pool:".format(max_workers))
        print("\tresults {} in {}s".format(response[:3]+["..."]+response[-3:], T))

    # Yet another way:
    @make_asynchronous
    def square(a):
        response = requests.get("http://api.mathjs.org/v4/", params={'expr':"{}^2".format(a)})
        return int(response.text)

    async def run():
        tasks = []
        # As before, we prepare the inputs
        for i in range(nb_inputs):
            print("square({})".format(i))
            tasks.append(square(i))
        # Then we wait for the results:
        for task in tasks:
            print(await task)
        # You could also use comprehensions to do this:
        response = [ await task for task in tasks ]
        print(response)

    loop = get_event_loop()
    loop.run_until_complete(run())
