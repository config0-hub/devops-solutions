def run(stackargs):

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

    # network related
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
    aws_base_network = {
        "name":"aws_base_network",
        "base":True,   # this indicates this is a base for other selectors
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
                           network_vars_set_labels_hash
                       ],
                       labels=[
                           general,
                           aws_cloud
                       ],
                       selectors=[
                           aws_base_network
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