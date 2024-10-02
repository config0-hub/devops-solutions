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
        "public_subnet_ids": "selector:::public_subnet_info::subnet_id:csv",
        "private_subnet_ids": "selector:::private_subnet_info::subnet_id:csv",
        "public_route_table_id": "selector:::public_route_table::route_table_id",
        "private_route_table_id": "selector:::private_route_table::route_table_id",
        "db_sg_id": "selector:::sg_database_info::sg_id",
        "bastion_sg_id": "selector:::sg_bastion_info::sg_id",
        "web_sg_id": "selector:::sg_web_info::sg_id",
        "api_sg_id": "selector:::sg_api_info::sg_id"
    }

    cloud_tags_hash = {
        "name":"cloud_tags_hash",
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
        "name":"network_vars_set_labels_hash",
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
        "name":"network_vars_set_arguments_hash",
        "values": {
            "arguments_hash": stack.b64_encode(_network_vars_arguments),
        }
    }

    ###########################################################
    # developer solutions/environment related arguments
    ###########################################################
    # the below is the same as above the variable is not
    # labels_hash or arguments_hash, but rather
    # netvars_set_arguments_hash
    # netvars_set_labels_hash

    netvars_set_labels_hash = {
        "name":"netvars_set_labels_hash",
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
        "name":"netvars_set_arguments_hash",
        "values": {
            "netvars_set_arguments_hash": stack.b64_encode(_network_vars_arguments)
        }
    }

    _env_network_values = {
        "vpc_id": "selector:::network_vars::vpc_id",
        "vpc_name": "selector:::vpc_info::vpc_name",
        "private_route_table_id": "selector:::private_route_table::route_table_id",
        "public_subnet_ids": "selector:::network_vars::public_subnet_ids:csv",
        "private_subnet_ids": "selector:::network_vars::private_subnet_ids:csv",
        "db_sg_id": "selector:::network_vars::db_sg_id",
        "eks_cluster_sg_id": "selector:::network_vars::bastion_sg_id",
        "eks_node_role_arn": "selector:::eks_info::node_role_arn"
    }

    # env sql
    env_sql_arguments = {
        "name":"env_sql_arguments",
        "values": {
            "db_engine": "MySQL",
            "db_engine_version": "5.7.44"
        }
    }

    env_sql_arguments["values"].update(_env_network_values)

    # env nosql
    env_nosql_arguments = {
        "name":"env_nosql_arguments",
        "values": {
            "mongodb_ami_filter": "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*",
            "mongodb_ami_owner": "099720109477",
            "bastion_ami_filter": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*",
            "bastion_ami_owner": "099720109477",
            "bastion_sg_id": "selector:::sg_bastion_info::sg_id",
            "bastion_subnet_ids": "selector:::public_subnet_info::subnet_id:csv"
        }
    }

    env_nosql_arguments["values"].update(_env_network_values)

    # env streaming
    env_streaming_arguments = {
        "name":"env_streaming_arguments",
        "values": {
            "bastion_ami_filter": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*",
            "bastion_ami_owner": "099720109477",
            "bastion_sg_id": "selector:::sg_bastion_info::sg_id",
            "bastion_subnet_ids": "selector:::public_subnet_info::subnet_id:csv",
            "kafka_ami_filter": "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*",
            "kafka_ami_owner": "099720109477",
            "kafka_instance_type": "t3.micro"
        }
    }

    env_streaming_arguments["values"].update(_env_network_values)

    #####################################################
    # stack labels
    #####################################################
    general = {
        "name":"general",
        "values":global_labels
    }

    aws_cloud = {
        "name":"aws_cloud",
        "values":{
            "provider":"aws",
            "cloudprovider": "aws"
        }
    }

    do_cloud = {
        "name":"do_cloud",
        "values":{
            "provider":"digitalocean",
            "cloudprovider": "digitalocean"
        }
    }

    #####################################################
    # stack selectors
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

    public_route_table = deepcopy(_aws_base_network_values)
    public_route_table["name"] = "public_route_table"
    public_route_table["values"]["matchParams"] = { "resource_type": "route_table" }
    public_route_table["values"]["matchKeys"] = { "public_route_table": True }

    private_route_table = deepcopy(_aws_base_network_values)
    private_route_table["name"] = "private_route_table"
    private_route_table["values"]["matchParams"] = { "resource_type": "route_table" }
    private_route_table["values"]["matchKeys"] = { "private_route_table": True }

    private_subnet_info = deepcopy(_aws_base_network_values)
    private_subnet_info["name"] = "private_subnet_info"
    private_subnet_info["values"]["matchParams"] = { "resource_type": "subnet" }
    private_subnet_info["values"]["matchKeys"] = { "name": "private" }

    public_subnet_info = deepcopy(_aws_base_network_values)
    public_subnet_info["name"] = "public_subnet_info"
    public_subnet_info["values"]["matchParams"] = { "resource_type": "subnet" }
    public_subnet_info["values"]["matchKeys"] = { "name": "public" }

    sg_database_info = deepcopy(_aws_base_network_values)
    sg_database_info["name"] = "sg_database_info"
    sg_database_info["values"]["matchParams"] = {"resource_type": "security_group"}
    sg_database_info["values"]["matchKeys"] = {"name": "database"}

    sg_bastion_info = deepcopy(_aws_base_network_values)
    sg_bastion_info["name"] = "sg_bastion_info"
    sg_bastion_info["values"]["matchParams"] = {"resource_type": "security_group"}
    sg_bastion_info["values"]["matchKeys"] = {"name": "bastion"}

    sg_web_info = deepcopy(_aws_base_network_values)
    sg_web_info["name"] = "sg_web_info"
    sg_web_info["values"]["matchParams"] = {"resource_type": "security_group"}
    sg_web_info["values"]["matchKeys"] = {"name": "web"}

    sg_api_info = deepcopy(_aws_base_network_values)
    sg_api_info["name"] = "sg_api_info"
    sg_api_info["values"]["matchParams"] = {"resource_type": "security_group"}
    sg_api_info["values"]["matchKeys"] = {"name": "api"}

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
                "region":aws_default_region
            },
            "matchParams": {
                "resource_type":"eks"
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
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
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
                           public_route_table,
                           private_route_table,
                           public_subnet_info,
                           private_subnet_info,
                           sg_bastion_info,
                           sg_database_info,
                           sg_web_info,
                           sg_api_info
                       ])

    # iac-ci with aws
    stack.add_substack('config0-publish:::setup_iac_ci',
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-publish:::register_repo_iac_ci',
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    #stack.add_substack('config0-publish:::add_iac_ci',
    #                   arguments=[
    #                       cloud_tags_hash
    #                   ],
    #                   labels=[
    #                       general,
    #                       aws_cloud
    #                   ],
    #                   inputvars=["infracost"])

    # ci with aws codebuild
    stack.add_substack('config0-publish:::setup_codebuild_ci',
                       arguments=[
                           cloud_tags_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       inputvars=["infracost"])

    stack.add_substack('config0-publish:::add_codebuild_ci',
                       arguments=[
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
        public_route_table,
        private_route_table,
        public_subnet_info,
        private_subnet_info,
        sg_bastion_info,
        sg_database_info,
        sg_web_info,
        sg_api_info
    ]

    stack.add_substack('config0-publish:::env_sql',
                       arguments=[
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
                       at_launch=["labels","selectors"])

    stack.add_substack('config0-publish:::env_nosql',
                       arguments=[
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
                       at_launch=["labels","selectors"])

    stack.add_substack('config0-publish:::env_streaming',
                       arguments=[
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
                       at_launch=["labels","selectors"])

    stack.init_substacks()

    return stack.get_results()
