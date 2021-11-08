import itertools
import threading
import numpy as np


class ThreadedFn:
    # lists of inputs for different threads
    # e.g., [[`input for thread 1`], [`input for thread 2`], ...]
    inputs = None
    # lists of outputs from different threads
    # e.g., [[`output from thread 1`], [`output from thread 2`], ...]
    outputs = None

    def __init__(self, num_threads, inputs):
        self.num_threads = num_threads
        self.inputs = inputs
        self._prepare_inputs()
        self._prepare_outputs()
        self._init_logger()

    def _init_logger(self):
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s| %(levelname)s| %(threadName)s] %(message)s")
        self.logger = logging
        
    def _prepare_inputs(self):
        inputs = np.array_split(self.inputs, self.num_threads)
        inputs = [x.tolist() for x in inputs]
        self.inputs = inputs

    def _prepare_outputs(self):
        self.outputs = [[] for _ in range(self.num_threads)]

    def _finialize_output(self, x):
        if isinstance(x, list):
            if len(x[0]) == 0:
                x[0] = [None]
            while isinstance(x[0], list):
                x = list(itertools.chain.from_iterable(x))
        return x

    def run(self):
        threads = []
        for i in range(self.num_threads):
            self.logger.info(f"Starting thread {i}")
            t = threading.Thread(target=self._run, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return self._finialize_output(self.outputs)

    def _run(self, thread_num):
        inputs = self.inputs[thread_num]
        len_inputs = len(inputs)
        out = []
        for i, _input in inputs:
            self.logger.info(f"{i + 1}/{len_inputs}")
            o = self.fn(_input)
            out.append(o)

        self.outputs[thread_num] = out

    def fn(self, d):
        return d["x"] + d["y"]
