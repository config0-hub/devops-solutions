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
    billing_tag = "eval-config0-2024"

    _global_labels = {
        "environment": "dev",
        "purpose": "eval-config0"
    }

    #####################################################
    # stack arguments
    #####################################################
    # cloud_tags arguments are passed
    # as b64 string as cloud_tags_hash
    cloud_tags = {
        "name":"cloud_tags",
        "values": {
            "cloud_tags_hash": stack.b64_encode({
                **_global_labels,
                "billing":billing_tag
            })
        }
    }

    # network related arguments
    network_vars_set_labels_hash = {
        "name":"network_vars_set_labels_hash",
        "values": {
            "labels_hash": stack.b64_encode({
                **_global_labels,
                "region": aws_default_region,
                "area": "network",
                "provider": "aws"
            })
        }
    }

    network_vars_set_arguments_hash = {
        "name":"network_vars_set_arguments_hash",
        "values": {
            "arguments_hash": stack.b64_encode({
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
            })
        }
    }

    #####################################################
    # stack labels
    #####################################################
    general = {
        "name":"general",
        "values":_global_labels
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
    # vars set stack specific variable set
    # special selector base
    _aws_base_network_values = {
        "values":{
            "matchKeys":{
                "provider":"aws"
            },
            "matchLabels": {
                **_global_labels,
                "area": "network"
            },
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
                **_global_labels,
                "region":aws_default_region,
                "area": "network",
                "provider":"aws"
            },
        }
    }

    eks_info = {
        "name": "eks_info",
        "values": {
            "matchLabels": {
                **_global_labels
            },
            "matchKeys": {
                "provider":"aws",
                "region":aws_default_region
            },
            "matchParams": {
                "resource_type":"eks"
            }
        }
    }

    #####################################################
    # default stacks and associate variables,
    # labels, and selectors
    #####################################################
    # vpc/network_vars_set for vpc setting
    stack.add_substack('config0-publish:::aws_vpc_simple',
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ])

    # related to mostly vpc
    stack.add_substack('config0-publish:::network_vars_set',
                       arguments=[
                           cloud_tags,
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

    # ci with aws codebuild
    stack.add_substack('config0-publish:::setup_codebuild_ci',
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ])

    stack.add_substack('config0-publish:::add_codebuild_ci',
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ])

    stack.add_substack('config0-publish:::aws_nat_inst_vpc',  # nat instance (instead of nat gw)
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ])

    stack.add_substack('config0-publish:::aws_nat_vpc',  # aws nat gateway saas
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ])

    # aws stateful stacks
    stack.add_substack('config0-publish:::aws_rds',
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ])

    stack.add_substack('config0-publish:::mongodb_replica_on_ec2',
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ])

    stack.add_substack('config0-publish:::kafka_on_ec2',
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars
                       ])

    # aws kubernetes
    stack.add_substack('config0-publish:::aws_eks',
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           network_vars,
                           eks_info
                       ])

    # digital ocean
    stack.add_substack("config0-publish:::jenkins_on_do",
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           do_cloud
                       ])

    stack.add_substack("config0-publish:::doks",
                       arguments=[cloud_tags],
                       labels=[
                           general,
                           do_cloud
                       ])

    # drift detection of resources
    stack.add_substack('config0-publish:::check_drift_resources',
                       arguments=[cloud_tags],
                       labels=[
                           general
                       ])

    stack.init_substacks()

    return stack.get_results()