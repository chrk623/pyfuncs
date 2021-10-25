from pyfuncs.threaded_fn import ThreadedFn


class NewThreadFn(ThreadedFn):
    def __init__(self, num_threads, inputs):
        super().__init__(num_threads, inputs)

    def fn(self, d):
        return d["x"] * d["y"]


inputs = [
    {
        "x": 1,
        "y": 2
    },
    {
        "x": 3,
        "y": 4
    },
    {
        "x": 5,
        "y": 6
    },
    {
        "x": 7,
        "y": 8
    },
    {
        "x": 9,
        "y": 10
    },
]

ts = NewThreadFn(num_threads=5, inputs=inputs)
out = ts.run()