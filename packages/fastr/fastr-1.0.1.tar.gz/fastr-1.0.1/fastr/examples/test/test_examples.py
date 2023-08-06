import os
import imp

import nose.tools as nt

import fastr


def test_examples():
    examples_dir = fastr.config.examplesdir
    examples = [os.path.join(examples_dir, x) for x in os.listdir(examples_dir) if x.endswith(".py")]
    for example_path in examples:
        if not example_path.endswith("__init__.py"):
            yield run, example_path


def run(example_path):
    example_base, _ = os.path.splitext(os.path.basename(example_path))
    example_module = imp.load_source(example_base, example_path)
    network = example_module.create_network()
    source_data = example_module.source_data(network)
    sink_data = example_module.sink_data(network)
    result = network.execute(source_data, sink_data)
    nt.ok_(result)




