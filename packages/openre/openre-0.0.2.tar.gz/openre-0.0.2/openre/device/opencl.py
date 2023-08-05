# -*- coding: utf-8 -*-
"""
Поддержка OpenCL устройств
"""
cl = None
try:
    import pyopencl as cl
except ImportError:
    pass
from openre.device.abstract import Device
from openre.templates import env
from openre.data_types import types, null
import numpy as np
from openre import synapses

class OpenCL(Device):
    """
    Устройства, поддерживающие OpenCL
    """
    def __init__(self, config):
        super(OpenCL, self).__init__(config)
        if cl is None:
            raise ImportError('Install PyOpenCL to support OpenCL devices')
        platform_id = self.config.get('platform', 0)
        device_type = self.config.get('device_type')
        if device_type:
            self.device = cl.get_platforms()[platform_id].get_devices(
                getattr(cl.device_type, 'CPU'))[self.config.get('device', 0)]
        else:
            self.device = cl.get_platforms()[platform_id] \
                    .get_devices()[self.config.get('device', 0)]
        # create an OpenCL context
        self.ctx = cl.Context([self.device], dev_type=None)
        self.queue = cl.CommandQueue(self.ctx)
        code = env.get_template("device/opencl.c").render(
            types=types,
            null=null
        )

        # compile the kernel
        self.program = cl.Program(self.ctx, code).build(
            options="-cl-denorms-are-zero " \
                    "-cl-no-signed-zeros " \
                    "-cl-finite-math-only"
        )


    def tick_neurons(self, domain):
        length = domain.neurons.length
        if not length:
            return
        self.program.tick_neurons(
            self.queue, (length,), None,
            # domain
            types.tick(domain.ticks),
            # layers
            domain.layers_vector.threshold.device_data_pointer,
            domain.layers_vector.relaxation.device_data_pointer,
            domain.layers_vector.spike_cost.device_data_pointer,
            domain.layers_vector.max_vitality.device_data_pointer,
            # neurons
            domain.neurons.level.device_data_pointer,
            domain.neurons.flags.device_data_pointer,
            domain.neurons.spike_tick.device_data_pointer,
            domain.neurons.layer.device_data_pointer,
            domain.neurons.vitality.device_data_pointer
        ).wait()

    def tick_synapses(self, domain):
        length = domain.neurons.length
        if not length:
            return
        self.program.tick_synapses(
            self.queue, (length,), None,
            # domain
            types.synapse_level(domain.learn_rate),
            types.synapse_level(domain.learn_threshold),
            types.tick(domain.spike_learn_threshold),
            types.tick(domain.spike_forget_threshold),
            # neurons
            domain.neurons.level.device_data_pointer,
            domain.neurons.flags.device_data_pointer,
            domain.neurons.spike_tick.device_data_pointer,
            # synapses
            domain.synapses.level.device_data_pointer,
            domain.synapses.pre.device_data_pointer,
            domain.synapses.post.device_data_pointer,
            domain.synapses.learn.device_data_pointer,
            domain.synapses.flags.device_data_pointer,
            # pre-neuron - synapse index
            domain.pre_synapse_index.key.device_data_pointer,
            domain.pre_synapse_index.value.device_data_pointer,
            # post-neuron - synapse index
            domain.post_synapse_index.key.device_data_pointer,
            domain.post_synapse_index.value.device_data_pointer
        ).wait()
        # download layers stats from device once
        # per domain.config['stat_size'] ticks
        if domain.ticks % domain.config['stat_size'] == 0:
            domain.stat_vector.data.fill(0)
            self.program.update_layers_stat(
                self.queue, (domain.neurons.length,), None,
                # domain
                types.tick(domain.ticks),
                types.address(domain.config['stat_size']),
                types.address(domain.stat_fields),
                # layers
                domain.layers_stat.device_data_pointer,
                domain.layers_vector.max_vitality.device_data_pointer,
                # neurons
                domain.neurons.flags.device_data_pointer,
                domain.neurons.spike_tick.device_data_pointer,
                domain.neurons.layer.device_data_pointer,
                domain.neurons.vitality.device_data_pointer
            ).wait()
            domain.layers_stat.from_device(self)
            stat_length = len(domain.stat_vector)
            for layer_address in range(len(domain.layers)):
                layer_stat_start = \
                        domain.stat_fields \
                        * layer_address
                domain.stat_vector.data += domain.layers_stat.data[
                    layer_stat_start : layer_stat_start + stat_length
                ]
            self.program.init_layers_stat(
                self.queue, (len(domain.layers_stat),), None,
                domain.layers_stat.device_data_pointer
            ).wait()
            # count synapses stats
            domain.stat_vector.to_device(self)
            self.program.update_synapses_stat(
                self.queue, (len(domain.synapses),), None,
                domain.stat_vector.device_data_pointer,
                # synapses
                domain.synapses.learn.device_data_pointer,
                domain.synapses.flags.device_data_pointer
            ).wait()
            domain.stat_vector.from_device(self)
            domain.stat_set('stat_size', domain.config['stat_size'])
            # 0 - total spikes (one per neuron) per self.config['stat_size']
            # ticks
            domain.stat_set('total_spikes', domain.stat_vector.data[0])
            # 1 - number of the dead neurons
            domain.stat_set('dead_neurons', domain.stat_vector.data[1])
            # 2 - number of synapses with flag IS_STRENGTHENED
            domain.stat_set('strengthened_synapses', domain.stat_vector.data[2])
            # 3 - neurons tiredness = sum(layer.max_vitality - neuron.vitality)
            domain.stat_set('neurons_tiredness', domain.stat_vector.data[3])
            # 4 - synapse learn level
            domain.stat_set('synapse_learn_level', domain.stat_vector.data[4])

    def tick_transmitter_index(self, domain):
        length = len(domain.transmitter_index.local_address)
        if not length:
            return
        self.program.tick_transmitter_index(
            self.queue, (length,), None,
            # transmitter_index
            domain.transmitter_index.local_address.device_data_pointer,
            domain.transmitter_index.flags.device_data_pointer,
            # neurons
            domain.neurons.flags.device_data_pointer,
        ).wait()

    def tick_receiver_index(self, domain):
        length = len(domain.receiver_index.local_address)
        if not length:
            return
        self.program.tick_receiver_index(
            self.queue, (length,), None,
            # transmitter_index
            domain.receiver_index.local_address.device_data_pointer,
            domain.receiver_index.flags.device_data_pointer,
            # neurons
            domain.neurons.flags.device_data_pointer,
        ).wait()

    def create(self, data):
        if not len(data):
            return None
        return cl.Buffer(
            self.ctx,
            cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=data
        )

    def upload(self, device_data_pointer, data, is_blocking=True):
        # Do not upload empty buffers
        if not len(data) or device_data_pointer is None:
            return
        cl.enqueue_copy(
            self.queue, device_data_pointer, data, is_blocking=is_blocking)

    def download(self, data, device_data_pointer, is_blocking=True):
        if device_data_pointer is None:
            return
        cl.enqueue_copy(
            self.queue, data, device_data_pointer, is_blocking=is_blocking)

def test_device():
    if cl is None:
        # skip test
        return
    from openre import OpenRE
    from pytest import raises
    import numpy as np
    from openre import neurons
    synapse_max_level = 30000
    config = {
        'synapse': {
            'max_level': synapse_max_level,
            'spike_learn_threshold': 2,
        },
        'layers': [
            {
                'name': 'V1',
                'threshold': synapse_max_level,
                'relaxation': 1000,
                'width': 20,
                'height': 20,
                'is_inhibitory': True,
                'connect': [
                    {
                        'name': 'V2',
                        'radius': 1,
                        'shift': [0, 0],
                    },
                ],
            },
            {
                'name': 'V2',
                'threshold': synapse_max_level,
                'relaxation': 1000,
                'width': 20,
                'height': 20,
            },
        ],
        'domains': [
            {
                'name'        : 'D1',
                'device'    : {
                    'type': 'OpenCL',
                },
                'stat_size': 1,
                'layers'    : [
                    {'name': 'V1'},
                    {'name': 'V2'},
                ],
            },
        ],
    }
    ore = OpenRE(config)
    ore.deploy()
    assert isinstance(ore.domains[0].device, OpenCL)
    assert ore.domains[0].neurons.level.device_data_pointer
    assert ore.domains[0].layers_vector.threshold.device_data_pointer
    domain = ore.domains[0]
    layer = domain.layers[0]
    layer2 = domain.layers[1]
    device = ore.domains[0].device
    max_vitality = types.max(types.vitality)

    # check lengths
    assert len(domain.synapses.level) == 400
    assert len(domain.synapses) == 400
    assert domain.neurons.length == 800
    assert layer.neurons_metadata.level.length == 400
    assert layer2.neurons_metadata.level.length == 400
    for field, field_type in domain.synapses_metadata.__class__.fields:
        assert getattr(domain.synapses_metadata, field).length == 400
        assert len(getattr(domain.synapses, field).data) == 400
    assert domain.pre_synapse_index.key.length == 800
    assert domain.pre_synapse_index.value.length == 400

    assert domain.post_synapse_index.key.length == 800
    assert domain.post_synapse_index.value.length == 400

    # prepare neurons
    layer.neurons_metadata.level[0, 0] = synapse_max_level
    assert not layer.neurons_metadata.flags[0, 0] & neurons.IS_SPIKED

    layer.neurons_metadata.level[0, 1] = layer.relaxation + 1
    layer.neurons_metadata.flags[0, 1] |= neurons.IS_SPIKED
    assert layer.neurons_metadata.flags[0, 1] | neurons.IS_SPIKED

    layer.neurons_metadata.level[0, 2] = synapse_max_level
    layer.neurons_metadata.flags[0, 2] |= neurons.IS_DEAD
    layer.neurons_metadata.flags[0, 2] |= neurons.IS_SPIKED

    layer.neurons_metadata.level[0, 3] = synapse_max_level
    layer.neurons_metadata.flags[0, 3] |= neurons.IS_RECEIVER
    layer.neurons_metadata.flags[0, 3] |= neurons.IS_SPIKED

    layer.neurons_metadata.level[0, 4] = -1

    layer.neurons_metadata.level[0, 5] = -1

    layer.neurons_metadata.level[0, 6] = synapse_max_level
    layer.neurons_metadata.vitality[0, 6] = layer.spike_cost

    layer.neurons_metadata.level[0, 7] = synapse_max_level
    layer2.neurons_metadata.level[0, 7] = synapse_max_level

    # synapses
    before = layer2.neurons_metadata.level[0, 0]
    synapse_address = domain.pre_synapse_index.key[0]
    synapse_level = domain.synapses.level[synapse_address]
    layer.neurons_metadata.level[1, 0] = synapse_max_level
    layer2.neurons_metadata.flags[1, 0] |= neurons.IS_DEAD
    layer2.neurons_metadata.level[1, 1] = synapse_max_level
    layer.neurons_metadata.flags[1, 2] |= neurons.IS_DEAD
    layer2.neurons_metadata.level[1, 2] = synapse_max_level

    l2_n_level_before = layer2.neurons_metadata.level[0, 0]

    layer2.neurons_metadata.level[0, 6] = synapse_max_level
    s_level_before_7 = domain.synapses.level[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(0, 7)
    ]]
    domain.synapses.learn[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(0, 7)
    ]] = domain.learn_threshold

    domain.neurons.to_device(device)
    domain.synapses.to_device(device)
    domain.tick()
    domain.neurons.from_device(device)
    domain.synapses.from_device(device)
    s_level = domain.synapses.level[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(0, 0)
    ]]
    if l2_n_level_before - layer2.relaxation < 0:
        res = np.int32(0) - s_level
        assert res == layer2.neurons_metadata.level[0, 0]
    else:
        assert l2_n_level_before - s_level - layer2.relaxation \
                == layer2.neurons_metadata.level[0, 0]

    # check neurons (layer.neurons_metadata.level[x, y])
    assert layer.neurons_metadata.level[0, 0] == 0
    assert layer.neurons_metadata.flags[0, 0] & neurons.IS_SPIKED
    assert layer.neurons_metadata.spike_tick[0, 0] == 1
    assert layer.neurons_metadata.vitality[0, 0] \
            == max_vitality - layer.spike_cost + 1

    assert layer.neurons_metadata.level[0, 1] == 1
    assert not layer.neurons_metadata.flags[0, 1] & neurons.IS_SPIKED
    assert layer.neurons_metadata.spike_tick[0, 1] == 0
    assert layer.neurons_metadata.vitality[0, 1] \
            == max_vitality

    assert layer.neurons_metadata.level[0, 2] == synapse_max_level
    assert layer.neurons_metadata.flags[0, 2] & neurons.IS_DEAD
    assert layer.neurons_metadata.flags[0, 2] & neurons.IS_SPIKED

    assert layer.neurons_metadata.level[0, 3] == synapse_max_level
    assert layer.neurons_metadata.flags[0, 3] & neurons.IS_RECEIVER
    assert not layer.neurons_metadata.flags[0, 3] & neurons.IS_SPIKED

    assert layer.neurons_metadata.level[0, 4] == 0

    assert layer.neurons_metadata.level[0, 5] == 0

    # spike and dies (low neuron.vitality)
    assert not layer.neurons_metadata.flags[0, 6] & neurons.IS_SPIKED
    assert layer.neurons_metadata.flags[0, 6] & neurons.IS_DEAD
    assert layer.neurons_metadata.vitality[0, 6] \
            == max_vitality

    # check synapses
    s_level_after_7 = domain.synapses.level[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(0, 7)
    ]]
    s_learn_after_7 = domain.synapses.learn[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(0, 7)
    ]]
    assert s_level_before_7 + domain.learn_threshold == s_level_after_7
    assert s_learn_after_7 <= domain.learn_rate
    assert domain.synapses.flags[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(0, 7)
    ]] & synapses.IS_STRENGTHENED
    assert not domain.synapses.flags[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(0, 0)
    ]] & synapses.IS_STRENGTHENED

    before = before - 1000
    if before < 0:
        before = 0
    # layer 1 is inhibitory
    assert layer2.neurons_metadata.level[0, 0] == before - synapse_level
    # dead post-neuron so synapse level should be 0
    assert domain.synapses.level[domain.pre_synapse_index.key[
        layer.neurons_metadata.level.to_address(1, 0)
    ]] == 0
    assert layer2.neurons_metadata.flags[1, 1] & neurons.IS_SPIKED
    # dead pre-neuron so synapse level should be 0
    assert domain.synapses.level[domain.post_synapse_index.key[
        layer2.neurons_metadata.level.to_address(1, 2)
    ]] == 0
    assert domain.synapses.learn[domain.pre_synapse_index.key[
        layer.neurons_metadata.level.to_address(0, 0)
    ]] == domain.learn_rate - 1
    # check stats
    for field_num in range(0, domain.stat_fields):
        if field_num not in [2, 4]:
            assert domain.stat_vector[0 + field_num] \
                == domain.layers_stat[0 + field_num] \
                + domain.layers_stat[ \
                    0 + field_num + len(domain.stat_vector)]

    assert domain.config['stat_size'] == domain.stat('stat_size')
    # field 0 - total spikes
    assert domain.stat_vector[0] >= 4
    assert domain.stat_vector[0] == domain.stat('total_spikes')
    assert domain.layers_stat[0] >= 2
    assert domain.layers_stat[0 + len(domain.stat_vector)] >= 2
    # field 1 - number of the dead neurons
    assert domain.layers_stat[1] == 3
    assert domain.stat_vector[1] == domain.stat('dead_neurons')
    assert domain.layers_stat[1 + len(domain.stat_vector)] == 1
    # field 2 - number of synapses with IS_STRENGTHENED flag
    assert domain.stat_vector[2] == 1
    assert domain.stat_vector[2] == domain.stat('strengthened_synapses')
    # field 3 - tiredness
    assert domain.layers_stat[3] \
            == (layer.spike_cost - 1) * domain.layers_stat[0]
    assert domain.layers_stat[3 + len(domain.stat_vector)] \
            == (layer2.spike_cost - 1) \
                * domain.layers_stat[0 + len(domain.stat_vector)]
    assert domain.stat_vector[3] == domain.stat('neurons_tiredness')
    # field 4 - sum(synapse.learn)
    assert domain.stat_vector[4] >= (domain.learn_rate - 1) * 3
    assert domain.stat_vector[4] == domain.stat('synapse_learn_level')

    # test kernel
    test_length = 15
    test_kernel = np.zeros((test_length,)).astype(np.uint32)
    test_kernel_buf = cl.Buffer(
            device.ctx,
            cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=test_kernel
        )

    device.program.test_kernel(
        device.queue, (test_length,), None,
        test_kernel_buf,
        np.int32(test_length)
    )
    cl.enqueue_copy(device.queue, test_kernel, test_kernel_buf)
    assert 8 | (3 & neurons.IS_SPIKED) == 10
    assert 8 | (1 & neurons.IS_SPIKED) == 8
    assert 7 & ~neurons.IS_SPIKED == 5
    assert 8 & ~neurons.IS_SPIKED == 8
    assert list(test_kernel) == [
        neurons.IS_INHIBITORY,
        neurons.IS_SPIKED,
        neurons.IS_DEAD,
        neurons.IS_TRANSMITTER,
        neurons.IS_RECEIVER,
        test_length,
        1, # 3 & IS_INHIBITORY
        2, # 3 & IS_SPIKED
        0, # 3 & IS_DEAD
        test_length,
        null,
        synapses.IS_STRENGTHENED,
        3,
        8 | (3 & neurons.IS_SPIKED),
        7 & ~neurons.IS_SPIKED,
    ]


    # remote domains
    config = {
        'synapse': {
            'max_level': synapse_max_level,
            'spike_learn_threshold': 2,
        },
        'layers': [
            {
                'name': 'V1',
                'threshold': synapse_max_level,
                'relaxation': 1000,
                'width': 20,
                'height': 20,
                'is_inhibitory': True,
                'connect': [
                    {
                        'name': 'V2',
                        'radius': 1,
                        'shift': [0, 0],
                    },
                ],
            },
            {
                'name': 'V2',
                'threshold': synapse_max_level,
                'relaxation': 1000,
                'width': 20,
                'height': 20,
            },
        ],
        'domains': [
            {
                'name'        : 'D1',
                'device'    : {
                    'type': 'OpenCL',
                },
                'layers'    : [
                    {'name': 'V1'},
                ],
            },
            {
                'name'        : 'D2',
                'device'    : {
                    'type': 'OpenCL',
                },
                'layers'    : [
                    {'name': 'V2'},
                ],
            },
        ],
    }
    ore = OpenRE(config)
    ore.deploy()
    d1 = ore.domains[0]
    d2 = ore.domains[1]
    v1 = d1.layers[0]
    v1.neurons_metadata.level[0, 0] = synapse_max_level
    d1.neurons.to_device(d1.device)
    d1.synapses.to_device(d1.device)
    d1.tick()
    d1.neurons.from_device(d1.device)
    d1.synapses.from_device(d1.device)
    d1.transmitter_index.flags.from_device(d1.device)
    assert v1.neurons_metadata.flags[0, 0] & neurons.IS_SPIKED
    assert v1.neurons_metadata.flags[0, 0] & neurons.IS_INHIBITORY
    assert d1.transmitter_index.flags[0] & neurons.IS_SPIKED
    assert d1.transmitter_index.flags[0] & neurons.IS_INHIBITORY

    assert d2.receiver_index.flags[0] & neurons.IS_SPIKED
    local_address = d2.receiver_index.local_address[0]
    assert local_address == 400
    assert not d2.neurons.flags[local_address] & neurons.IS_SPIKED
    assert d2.neurons.flags[local_address] & neurons.IS_INHIBITORY
    assert d2.neurons.flags[local_address] & neurons.IS_RECEIVER
    d2.tick()
    d2.neurons.from_device(d2.device)
    assert not d2.receiver_index.flags[0] & neurons.IS_SPIKED
    assert d2.neurons.flags[local_address] & neurons.IS_SPIKED
    assert d2.neurons.flags[local_address] & neurons.IS_INHIBITORY
    assert d2.neurons.flags[local_address] & neurons.IS_RECEIVER

