"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

def run(stackargs):

    from copy import deepcopy

    '''
    this is platform versioning example
    for the starting out guide
    '''

    # instantiate authoring stack
    stack = newStack(stackargs)

    # important to classify this stack
    # as a platform stack/configuration
    stack.set_platform()

    #####################################################
    # specific vars for platform
    #####################################################
    # we use us-east-1 since most of our s3 buckets are here
    # so for lambda functions and storing them. it's better
    # to keep it for the evaluation and demo in this region
    aws_default_region = "eu-west-1"

    global_labels = {
        "environment": "dev",
        "purpose": "eval-config0"
    }

    env_global_labels = {
        "environment": "dev",
        "purpose": "eval-config0-env"
    }

    # env_nosql runs in its own purpose namespace so its records never collide
    # with env_sql's - the two are independent stories and either can be live
    # while the other is torn down.
    nosql_global_labels = {
        "environment": "dev",
        "purpose": "eval-config0-nosql"
    }

    billing_tag = "eval-config0-2024"

    #####################################################
    # stack arguments
    #####################################################

    # network vars single run
    _network_vars_labels = {
        **global_labels,
        "region": aws_default_region,
        "area": "network",
        "provider": "aws"
    }

    _network_vars_arguments = {
        "vpc_name": "selector:::vpc_info::name",
        "vpc_id": "selector:::vpc_info::vpc_id",
        "public_subnet_ids": "selector:::vpc_info::public_subnet_ids",
        "private_subnet_ids": "selector:::vpc_info::private_subnet_ids",
        "public_route_table_id": "selector:::vpc_info::public_route_table_id",
        "private_route_table_id": "selector:::vpc_info::private_route_table_id",
        "db_sg_id": "selector:::sg_info::db_sg_id",
        "bastion_sg_id": "selector:::sg_info::bastion_sg_id",
        "web_sg_id": "selector:::sg_info::web_sg_id",
        "api_sg_id": "selector:::sg_info::api_sg_id"
    }

    cloud_tags_hash = {
        "name": "cloud_tags_hash",
        "values": {
            "cloud_tags_hash": {
                **global_labels,
                "billing": billing_tag
            }
        },
        "at_launch": {
            "labels": {
                "fields": {
                    "cloud_tags_hash": {
                        "to_base64": True,
                        "insert": "*"
                    }
                }
            }
        }
    }

    env_cloud_tags_hash = deepcopy(cloud_tags_hash)
    env_cloud_tags_hash["values"]["cloud_tags_hash"] = {
        **env_global_labels,
        "billing": billing_tag
    }

    nosql_cloud_tags_hash = deepcopy(cloud_tags_hash)
    nosql_cloud_tags_hash["values"]["cloud_tags_hash"] = {
        **nosql_global_labels,
        "billing": billing_tag
    }

    # network related arguments
    network_vars_set_labels_hash = {
        "name": "network_vars_set_labels_hash",
        "values": {
            "labels_hash": _network_vars_labels
        },
        "at_launch": {
            "labels": {
                "fields": {
                    "labels_hash": {
                        "to_base64": True,
                        "insert": "*"
                    }
                }
            }
        }
    }

    network_vars_set_arguments_hash = {
        "name": "network_vars_set_arguments_hash",
        "values": {
            "arguments_hash": stack.serialize(_network_vars_arguments, json=False),
        }
    }

    aws_default_region_args = {
        "name": aws_default_region,
        "values": {
            "aws_default_region": aws_default_region
        }
    }

    ###########################################################
    # Developer Environment Configuration
    ###########################################################
    # IMPORTANT NAMING CONVENTION:
    # When working with network variable hashes in this section:
    # - Use 'netvars_set_arguments_hash' (NOT 'arguments_hash')
    # - Use 'netvars_set_labels_hash' (NOT 'labels_hash')
    # This maintains consistency with the parameter naming patterns
    # established in the rest of the codebase.
    ###########################################################

    netvars_set_labels_hash = {
        "name": "netvars_set_labels_hash",
        "values": {
            "netvars_set_labels_hash": _network_vars_labels
        },
        "at_launch": {
            "labels": {
                "fields": {
                    "netvars_set_labels_hash": {
                        "to_base64": True,
                        "insert": "*"
                    }
                }
            }
        }
    }

    env_netvars_set_labels_hash = deepcopy(netvars_set_labels_hash)
    env_netvars_set_labels_hash["values"]["netvars_set_labels_hash"] = {
        **env_global_labels,
        "region": aws_default_region,
        "area": "network",
        "provider": "aws"
    }

    nosql_netvars_set_labels_hash = deepcopy(netvars_set_labels_hash)
    nosql_netvars_set_labels_hash["values"]["netvars_set_labels_hash"] = {
        **nosql_global_labels,
        "region": aws_default_region,
        "area": "network",
        "provider": "aws"
    }

    netvars_set_arguments_hash = {
        "name": "netvars_set_arguments_hash",
        "values": {
            "netvars_set_arguments_hash": stack.serialize(_network_vars_arguments, json=False)
        }
    }

    _env_network_values = {
        "vpc_id": "selector:::network_vars::vpc_id",
        "vpc_name": "selector:::vpc_info::vpc_name",
        "private_route_table_id": "selector:::vpc_info::private_route_table_id",
        "public_subnet_ids": "selector:::network_vars::public_subnet_ids",
        "private_subnet_ids": "selector:::network_vars::private_subnet_ids",
        "db_sg_id": "selector:::network_vars::db_sg_id",
        "eks_cluster_sg_id": "selector:::network_vars::bastion_sg_id",
        "eks_node_role_arn": "selector:::eks_info::node_role_arn"
    }

    # env sql
    env_sql_arguments = {
        "name": "env_sql_arguments",
        "values": {
            "db_engine": "MySQL",
            "db_engine_version": "8.0.46"
        }
    }

    env_sql_arguments["values"].update(_env_network_values)

    # env nosql
    # no bastion host: the mongodb replicas are configured over the ssm executor
    # installed once per region by server-config (see _docs/README.md). the four
    # keys below are read off that install + its keypair, exactly the way
    # _env_network_values reads network_vars/sg_info for env_sql.
    _server_config_values = {
        "ssh_key_name": "selector:::keypair_vars::key_name",
        "instance_profile_name": "selector:::install_vars::instance_profile_name",
        "managed_tag_key": "selector:::install_vars::managed_tag_key",
        "managed_tag_value": "selector:::install_vars::managed_tag_value",
        "install_name": "selector:::install_vars::install_name"
    }

    env_nosql_arguments = {
        "name": "env_nosql_arguments",
        "values": {
            **_server_config_values
        }
    }

    env_nosql_arguments["values"].update(_env_network_values)

    # env streaming
    env_streaming_arguments = {
        "name": "env_streaming_arguments",
        "values": {
            "bastion_sg_id": "selector:::sg_info::bastion_sg_id",
            "bastion_subnet_ids": "selector:::vpc_info::public_subnet_ids",
            "kafka_instance_type": "t3.micro"
        }
    }

    env_streaming_arguments["values"].update(_env_network_values)

    # mongodb replica set, standalone catalogue child. same server-config
    # prerequisites as env_nosql, under this stack's own key names.
    mongodb_replica_arguments = {
        "name": "mongodb_replica_arguments",
        "values": {
            **_server_config_values
        }
    }

    #####################################################
    # stack labels
    #####################################################
    general = {
        "name": "general",
        "values": global_labels
    }

    env_general = {
        "name": "general",
        "values": env_global_labels
    }

    nosql_general = {
        "name": "general",
        "values": nosql_global_labels
    }

    aws_cloud = {
        "name": "aws_cloud",
        "values": {
            "provider": "aws",
            "cloudprovider": "aws"
        }
    }

    do_cloud = {
        "name": "do_cloud",
        "values": {
            "provider": "digitalocean",
            "cloudprovider": "digitalocean"
        }
    }

    #####################################################
    # stack selectors
    #####################################################

    #####################################################
    # not used very often
    # kept here only for backwards compatibility/reference
    #####################################################
    # at_launch is only need for entire environments
    # otherwise, the selectors will fail if not
    # connected to the same project or launch instance
    #_aws_base_network_values = {
    #    "values": {
    #        "matchLabels": {
    #            **global_labels
    #        }
    #    },
    #    "at_launch": _at_launch
    #}
    #####################################################

    _aws_base_network_match = {
        "match": {
            "labels": {
                **global_labels
            }
        }
    }

    aws_base_network = deepcopy(_aws_base_network_match)
    aws_base_network["name"] = "aws_base_network"
    aws_base_network["base"] = True

    vpc_info = deepcopy(_aws_base_network_match)
    vpc_info["name"] = "vpc_info"
    vpc_info["match"]["filter"] = {"resource_type": "vpc"}

    sg_info = deepcopy(_aws_base_network_match)
    sg_info["name"] = "sg_info"
    sg_info["match"]["filter"] = {"resource_type": "security_group"}

    network_vars = {
        "name": "network_vars",
        "match": {
            "labels": {
                **global_labels
            },
            "filter": {
                "resource_type": "vars_set"
            }
        }
    }

    # region prerequisites, installed once per region by server-config. unlike the
    # env_* forward references these match records that ALREADY exist, so they are
    # never folded into env_selectors and carry no at_launch identity stamp.
    _server_config_match_labels = {
        "purpose": "server-configuration",
        "region": aws_default_region
    }

    keypair_vars = {
        "name": "keypair_vars",
        "match": {
            "labels": {
                **_server_config_match_labels
            },
            "filter": {
                "resource_type": "ssh_key_pair"
            }
        }
    }

    install_vars = {
        "name": "install_vars",
        "match": {
            "labels": {
                **_server_config_match_labels
            },
            "filter": {
                "resource_type": "ssm_ec2_exec_eventbridge_install"
            }
        }
    }

    eks_info = {
        "name": "eks_info",
        "match": {
            "labels": {
                **global_labels
            },
            "keys": {
                "region": aws_default_region
            },
            "filter": {
                "resource_type": "eks"
            },
            "expect": {"optional": True}
        }
    }

    #####################################################
    # stacks allowed
    #####################################################

    # Individual IaCs
    # vpc/network_vars_set for vpc setting
    stack.add_substack('config0-hub:::aws_networking::aws_vpc_simple',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           vpc_info,
                           network_vars
                       ],
                       inputvars=["infracost"])

    # related to mostly vpc
    stack.add_substack('config0-hub:::config0_core::network_vars_set',
                       arguments=[
                           cloud_tags_hash,
                           network_vars_set_labels_hash,
                           network_vars_set_arguments_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           aws_base_network,
                           vpc_info,
                           sg_info
                       ])

    # iac-ci with aws
    stack.add_substack('config0-hub:::devops-solutions::setup_iac_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-hub:::devops-solutions::register_repo_iac_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-hub:::devops-solutions::add_iac_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    # ci with aws codebuild
    stack.add_substack('config0-hub:::devops-solutions::setup_codebuild_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-hub:::devops-solutions::add_codebuild_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-hub:::aws_networking::aws_nat_inst_vpc',  # nat instance (instead of nat gw)
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-hub:::aws_networking::aws_nat_vpc',  # aws nat gateway saas
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ],
                       inputvars=["infracost"])

    # aws stateful stacks
    stack.add_substack('config0-hub:::aws_storage::aws_rds',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-hub:::mongodb::mongodb_replica_on_ec2',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash,
                           mongodb_replica_arguments
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars,
                           keypair_vars,
                           install_vars
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-hub:::kafka::kafka_on_ec2',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ],
                       inputvars=["infracost"])

    # aws kubernetes
    stack.add_substack('config0-hub:::aws_eks::aws_eks',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars,
                           eks_info
                       ],
                       inputvars=["infracost"])

    # aws kubernetes v2 (EKS with External DNS and ArgoCD)
    stack.add_substack('config0-hub:::aws_eks::aws_eks2',
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    # digital ocean
    stack.add_substack("config0-hub:::do::jenkins_on_do",
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           do_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack("config0-hub:::do::doks",
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           do_cloud
                       ],
                       inputvars=["infracost"])

    # drift detection of resources
    stack.add_substack('config0-hub:::config0_core::check_drift_resources',
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general
                       ])

    env_selectors = deepcopy([
        network_vars,
        eks_info,
        aws_base_network,
        vpc_info,
        sg_info
    ])
    for selector in env_selectors:
        selector["match"]["labels"] = {
            **env_global_labels
        }
        # at_launch stamps these with the run identity, so they can only match
        # records this run writes - always a forward reference at parent dispatch
        selector["match"]["expect"] = {"optional": True}

    stack.add_substack('config0-hub:::devops-solutions::env_sql',
                       arguments=[
                           aws_default_region_args,
                           env_cloud_tags_hash,
                           env_sql_arguments,
                           netvars_set_arguments_hash,
                           env_netvars_set_labels_hash
                       ],
                       labels=[
                           env_general
                       ],
                       selectors=env_selectors,
                       inputvars=["infracost"],
                       at_launch=["labels", "selectors"])

    # env_nosql also reads the two server-config prerequisites, which match
    # records that ALREADY exist and must NOT carry the launching project's
    # identity. at_launch=["labels", "selectors"] stamps EVERY selector on the
    # entry (scan_stacks/substack_catalogue.py:132-140 overwrites each one), so
    # this child declares at_launch=["labels"] and stamps its own five forward
    # references explicitly, leaving keypair_vars/install_vars unstamped.
    env_nosql_selectors = deepcopy(env_selectors)
    for selector in env_nosql_selectors:
        # own purpose namespace, so 109 never matches a live 105 record
        selector["match"]["labels"] = {
            **nosql_global_labels
        }
        selector["at_launch"] = {"labels": {"fields": {"_": {"insert": "*"}}}}
    env_nosql_selectors += [keypair_vars, install_vars]

    stack.add_substack('config0-hub:::devops-solutions::env_nosql',
                       arguments=[
                           aws_default_region_args,
                           nosql_cloud_tags_hash,
                           env_nosql_arguments,
                           netvars_set_arguments_hash,
                           nosql_netvars_set_labels_hash
                       ],
                       labels=[
                           nosql_general
                       ],
                       selectors=env_nosql_selectors,
                       inputvars=["infracost"],
                       at_launch=["labels"])

    stack.add_substack('config0-hub:::devops-solutions::env_streaming',
                       arguments=[
                           aws_default_region_args,
                           env_cloud_tags_hash,
                           env_streaming_arguments,
                           netvars_set_arguments_hash,
                           env_netvars_set_labels_hash
                       ],
                       labels=[
                           env_general
                       ],
                       inputvars=["infracost"],
                       selectors=env_selectors,
                       at_launch=["labels", "selectors"])

    stack.init_substacks()

    return stack.get_results()
