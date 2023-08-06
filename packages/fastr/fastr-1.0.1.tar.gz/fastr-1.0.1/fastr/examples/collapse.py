#!/usr/bin/env python


def create_network():
    # Import the faster environment and set it up
    import fastr
    # Create a new network
    network = fastr.Network(id_='collapse')

    # Create a source node in the network
    source = network.create_source(fastr.typelist['Int'], id_='source')

    # Create a sink to save the data
    sink = network.create_sink(fastr.typelist['Int'], id_='sink')

    # Link the addint node to the sink
    link = network.create_link(source.output, sink.input)
    link.collapse = 0

    return network


def source_data(network):
    return {
        'source': {
            'sample_a': (1, 2, 3, 4),
            'sample_b': (5, 6, 7, 8),
            'sample_c': (9, 10, 11, 12),
        }
    }


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Execute
    network.draw_network()
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
