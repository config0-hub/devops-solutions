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
            "arguments_hash": stack.b64_encode(_network_vars_arguments),
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

    netvars_set_arguments_hash = {
        "name": "netvars_set_arguments_hash",
        "values": {
            "netvars_set_arguments_hash": stack.b64_encode(_network_vars_arguments)
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
            "db_engine_version": "5.7.44"
        }
    }

    env_sql_arguments["values"].update(_env_network_values)

    # env nosql
    env_nosql_arguments = {
        "name": "env_nosql_arguments",
        "values": {
            "bastion_sg_id": "selector:::sg_info::bastion_sg_id",
            "bastion_subnet_ids": "selector:::vpc_info::public_subnet_ids",
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

    #####################################################
    # stack labels
    #####################################################
    general = {
        "name": "general",
        "values": global_labels
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

    _aws_base_network_values = {
        "values": {
            "matchLabels": {
                **global_labels
            }
        }
    }

    aws_base_network = deepcopy(_aws_base_network_values)
    aws_base_network["name"] = "aws_base_network"
    aws_base_network["base"] = True

    vpc_info = deepcopy(_aws_base_network_values)
    vpc_info["name"] = "vpc_info"
    vpc_info["values"]["matchParams"] = { "resource_type": "vpc" }

    sg_info = deepcopy(_aws_base_network_values)
    sg_info["name"] = "sg_info"
    sg_info["values"]["matchParams"] = {"resource_type": "security_group"}

    network_vars = {
        "name": "network_vars",
        "values": {
            "matchLabels": {
                **global_labels
            },
            "matchParams": {
                "resource_type": "vars_set"
            }
        }
    }

    eks_info = {
        "name": "eks_info",
        "values": {
            "matchLabels": {
                **global_labels
            },
            "matchKeys": {
                "region": aws_default_region
            },
            "matchParams": {
                "resource_type": "eks"
            }
        }
    }

    #####################################################
    # stacks allowed
    #####################################################

    # Individual IaCs
    # vpc/network_vars_set for vpc setting
    stack.add_substack('config0-publish:::aws_vpc_simple',
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
    stack.add_substack('config0-publish:::network_vars_set',
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
    stack.add_substack('config0-publish:::setup_iac_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-publish:::register_repo_iac_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-publish:::add_iac_ci',
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
    stack.add_substack('config0-publish:::setup_codebuild_ci',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-publish:::add_codebuild_ci',
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

    stack.add_substack('config0-publish:::aws_nat_inst_vpc',  # nat instance (instead of nat gw)
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

    stack.add_substack('config0-publish:::aws_nat_vpc',  # aws nat gateway saas
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
    stack.add_substack('config0-publish:::aws_rds',
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

    stack.add_substack('config0-publish:::mongodb_replica_on_ec2',
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

    stack.add_substack('config0-publish:::kafka_on_ec2',
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
    stack.add_substack('config0-publish:::aws_eks',
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
    stack.add_substack('config0-publish:::aws_eks2',
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    # digital ocean
    stack.add_substack("config0-publish:::jenkins_on_do",
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           do_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack("config0-publish:::doks",
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           do_cloud
                       ],
                       inputvars=["infracost"])

    # drift detection of resources
    stack.add_substack('config0-publish:::check_drift_resources',
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general
                       ])

    env_selectors = [
        network_vars,
        eks_info,
        aws_base_network,
        vpc_info,
        sg_info
    ]

    stack.add_substack('config0-publish:::env_sql',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash,
                           env_sql_arguments,
                           netvars_set_arguments_hash,
                           netvars_set_labels_hash
                       ],
                       labels=[
                           general
                       ],
                       selectors=env_selectors,
                       inputvars=["infracost"],
                       at_launch=["labels", "selectors"])

    stack.add_substack('config0-publish:::env_nosql',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash,
                           env_nosql_arguments,
                           netvars_set_arguments_hash,
                           netvars_set_labels_hash
                       ],
                       labels=[
                           general
                       ],
                       selectors=env_selectors,
                       inputvars=["infracost"],
                       at_launch=["labels", "selectors"])

    stack.add_substack('config0-publish:::env_streaming',
                       arguments=[
                           aws_default_region_args,
                           cloud_tags_hash,
                           env_streaming_arguments,
                           netvars_set_arguments_hash,
                           netvars_set_labels_hash
                       ],
                       labels=[
                           general
                       ],
                       inputvars=["infracost"],
                       selectors=env_selectors,
                       at_launch=["labels", "selectors"])

    stack.init_substacks()

    return stack.get_results()
