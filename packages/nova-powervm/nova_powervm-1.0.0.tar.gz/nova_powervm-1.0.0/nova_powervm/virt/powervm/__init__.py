# Copyright 2014, 2015 IBM Corp.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg

pvm_opts = [
    cfg.FloatOpt('proc_units_factor',
                 default=0.1,
                 help='Factor used to calculate the processor units per vcpu. '
                 'Valid values are: 0.05 - 1.0'),
    cfg.IntOpt('uncapped_proc_weight',
               default=64,
               help='The processor weight to assign to newly created VMs.  '
                    'Value should be between 1 and 255.  Represents how '
                    'aggressively LPARs grab CPU when unused cycles are '
                    'available.'),
    cfg.StrOpt('vopt_media_volume_group',
               default='rootvg',
               help='The volume group on the system that should be used '
                    'to store the config drive metadata that will be attached '
                    'to VMs.'),
    cfg.IntOpt('vopt_media_rep_size',
               default=1,
               help='The size of the media repository (in GB) for the '
                    'metadata for config drive.  Only used if the media '
                    'repository needs to be created.'),
    cfg.StrOpt('image_meta_local_path',
               default='/tmp/cfgdrv/',
               help='The location where the config drive ISO files should be '
                    'built.'),
    cfg.StrOpt('disk_driver',
               default='localdisk',
               help='The disk driver to use for PowerVM disks. '
               'Valid options are: localdisk, ssp')
]


CONF = cfg.CONF
CONF.register_opts(pvm_opts, group='powervm')

# Options imported from other regions
CONF.import_opt('host', 'nova.netconf')
CONF.import_opt('my_ip', 'nova.netconf')
CONF.import_opt('vncserver_proxyclient_address', 'nova.vnc', group='vnc')
CONF.import_opt('vncserver_listen', 'nova.vnc', group='vnc')


# NPIV Options.  Only applicable if the 'fc_attach_strategy' is set to 'npiv'.
# Otherwise this section can be ignored.
npiv_opts = [
    cfg.IntOpt('ports_per_fabric', default=1,
               help='The number of physical ports that should be connected '
                    'directly to the Virtual Machine, per fabric.  '
                    'Example: 2 fabrics and ports_per_fabric set to 2 will '
                    'result in 4 NPIV ports being created, two per fabric. '
                    'If multiple Virtual I/O Servers are available, will '
                    'attempt to span ports across I/O Servers.'),
    cfg.StrOpt('fabrics', default='A',
               help='Unique identifier for each physical FC fabric that is '
                    'available.  This is a comma separated list.  If there '
                    'are two fabrics for multi-pathing, then this could be '
                    'set to A,B.'
                    'The fabric identifiers are used for the '
                    '\'fabric_<identifier>_port_wwpns\' key.')
]
CONF.register_opts(npiv_opts, group='powervm')

# Dictionary where the key is the NPIV Fabric Name, and the value is a list of
# Physical WWPNs that match the key.
NPIV_FABRIC_WWPNS = {}

# At this point, the fabrics should be specified.  Iterate over those to
# determine the port_wwpns per fabric.
if CONF.powervm.fabrics is not None:
    port_wwpn_keys = []
    help_text = ('A comma delimited list of all the physical FC port WWPNs '
                 'that support the specified fabric.  Is tied to the NPIV '
                 'fabrics key.')

    fabrics = CONF.powervm.fabrics.split(',')
    for fabric in fabrics:
        opt = cfg.StrOpt('fabric_%s_port_wwpns' % fabric,
                         default='', help=help_text)
        port_wwpn_keys.append(opt)

    CONF.register_opts(port_wwpn_keys, group='powervm')

    # Now that we've registered the fabrics, saturate the NPIV dictionary
    for fabric in fabrics:
        key = 'fabric_%s_port_wwpns' % fabric
        wwpns = CONF.powervm[key].split(',')
        wwpns = [x.upper().strip(':') for x in wwpns]
        NPIV_FABRIC_WWPNS[fabric] = wwpns
