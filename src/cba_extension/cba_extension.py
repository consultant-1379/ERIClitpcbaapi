#
# COPYRIGHT Ericsson AB 2013
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#

from litp.core.model_type import (ItemType, Property, PropertyType,
                                  Reference, RefCollection, Collection)
from litp.core.extension import ModelExtension
from litp.core.validators import ItemValidator, ValidationError

from litp.core.litp_logging import LitpLogger
log = LitpLogger()


class LsbRuntimeValidator(ItemValidator):
    """
    Custom ItemValidator for lsb-runtime item type.

    Ensures that the status_interval and status_timeout attributes are
    integers with a value >= 10 and <= 3600.
    """
    def validate(self, properties):
        def ret_error(prop_name):
            err_msg = "The property '%s' must be "\
                "an integer with value >= 10 and <= 3600" % prop_name
            return ValidationError(
                property_name=prop_name,
                error_message=err_msg)
        props = ('status_interval', 'status_timeout')
        for prop_name in props:
            prop_int = None
            if prop_name in properties:
                prop_val = properties.get(prop_name)
                try:
                    prop_int = int(prop_val)
                except ValueError:
                    return ret_error(prop_name)
                if not (10 <= prop_int <= 3600):
                    return ret_error(prop_name)


class CBAExtension(ModelExtension):
    """
    The CBA (Component Based Architecture) Model Extension allows for the
    modelling of items to facilitate the install and configuration
    of Ericsson CBA Products e.g. Core Middleware.
    """

    def define_property_types(self):
        netname_re = r"[a-zA-Z][a-zA-Z0-9._-]*"
        csv_re = r"^(%s|(%s,)+%s)$" % (netname_re, netname_re, netname_re)

        property_types = [
            PropertyType("pkg_version", regex=r"^R[A-Z0-9]+$"),
            PropertyType("cluster_id", regex=r"^[0-9]+$"),
            PropertyType("quick_reboot", regex=r"^on|off$"),
        ]
        property_types.append(PropertyType("cmw_net_names",
                                            regex=csv_re))
        return property_types

    def define_item_types(self):
        item_types = [
            ItemType(
                "cmw-cluster",
                extend_item='cluster',
                item_description=("This item type represents a cluster "
                                  "of nodes with high availability, where "
                                  "the HA manager is provided by CMW "
                                  "(Core MiddleWare).  No reconfiguration "
                                  "actions are currently supported for "
                                  "this item type."),
                validators=[CmwClusterValidator()],
                cluster_id=Property("cluster_id", required=True,
                                    site_specific=True,
                                    prop_description=("Unique number to "
                                                      "identify Cluster")),
                internal_network=Property("basic_string",
                                          prop_description="Network to use as "
                                          "the internal network for LDE. LDE "
                                          "requires that an internal network "
                                          "is defined in its configuration. "
                                          "The internal network is used for "
                                          "various network services that can "
                                          "be provided by LDE.",
                                          required=True),
                tipc_networks=Property("cmw_net_names",
                                      prop_description="Comma separated list "
                                      "of network names to use as TIPC links.",
                                      required=True),
                quick_reboot=Property("quick_reboot", default='off',
                                      prop_description=("Set if BIOS is to be "
                                                        "bypassed at boot "
                                                        "time")),
                admin_op_timeout=Property(
                    "integer",
                    default="1800",
                    prop_description=("Maximum time, in seconds, for "
                                      "administrative operations while "
                                      "running a campaign")
                ),
                campaign_reboot_timeout=Property(
                    "integer",
                    default="2100",
                    prop_description=("Maximum time, in seconds, to wait for "
                                      "a node to reboot while running a "
                                      "campaign")
                ),
                cli_timeout=Property(
                    "integer",
                    default="2100",
                    prop_description=("Maximum time, in seconds, to wait for "
                                      "a cli command to execute")
                ),
                max_time_leaving_cluster=Property(
                    "integer",
                    default="35",
                    prop_description=("Maximum time, in minutes, to wait for "
                                      "a node to rejoin the cluster")
                ),
                imm_command_timeout=Property(
                    "integer",
                    default="900",
                    prop_description=("Maximum time, in seconds, to wait for "
                                      "a IMM command to finish")
                ),
            ),
            ItemType(
                "jee-deployable-entity",
                item_description="This item type represents a JEE (Java "
                "Platform, Enterprise Edition) deployable entity "
                "(application). No reconfiguration actions are currently "
                "supported for this item type.",
                extend_item="deployable-entity",
                name=Property(
                    "basic_string",
                    prop_description="Name of the Deployable entity",
                    required=True,
                ),
                package=Reference("package"),
                install_source=Property(
                    "path_string",
                    prop_description="Path to the file delivered by package",
                    required=True,
                ),
            ),
            ItemType(
                "lsb-runtime",
                deprecated=True,
                extend_item="runtime-entity",
                item_description="This item type represents an LSB-compliant "
                "service runtime. Deprecated.",
                validators=[LsbRuntimeValidator()],
                name=Property('basic_string',
                    prop_description="Old name of service (Do not use)."),
                service_name=Property(
                    'basic_string',
                    required=True,
                    prop_description="Name of the service to be called to "
                    "start/stop/status"),
                status_interval=Property(
                    "integer",
                    prop_description=("Value, in seconds, of the interval "
                                      "between status checks")
                ),
                status_timeout=Property(
                    "integer",
                    prop_description=("Value, in seconds, of the max "
                                      "duration of a status check")
                ),
                restart_limit=Property(
                    "integer",
                    prop_description=("Number of times an attempt should be "
                                      "made to restart a failed application")
                ),
                startup_retry_limit=Property(
                    "integer",
                    prop_description=("Number of times an attempt should be "
                                      "made to start an application")
                ),
                ipaddresses=Collection("vip"),
                filesystems=RefCollection("file-system")
            ),
            ItemType(
                "cmw-clustered-service",
                extend_item="clustered-service",
                item_description="This item type represents a service (an "
                "application resource) which runs on nodes in the cluster "
                "and which uses the CMW HA (Core MiddleWare high "
                "availability) manager that controls the cluster. "
                "No reconfiguration actions are currently supported "
                "for this item type.",
            )
        ]
        return item_types


class CmwClusterValidator(ItemValidator):
    def validate(self, properties):
        """Validates following constraints:
            - HB networks are not duplicated
        """

        hb_nets = properties.get("tipc_networks")
        mgmt_net = properties.get("internal_network")
        if not hb_nets or not mgmt_net:
            return

        if len(mgmt_net.split(",")) > 1:
            return ValidationError(
                    property_name="internal_network",
                    error_message="TIPC internal link should not be a"
                    " list")

        nets_all = hb_nets.split(",")
        dups = set([x for x in nets_all if nets_all.count(x) > 1])
        if dups:
            return ValidationError(
                    property_name="tipc_networks",
                    error_message=("Cannot create more than one TIPC link for "
                                    "the same network")
                            )
