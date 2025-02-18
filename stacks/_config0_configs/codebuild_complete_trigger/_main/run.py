from config0_publisher.terraform import TFConstructor


def run(stackargs):

    # instantiate authoring stack
    stack = newStack(stackargs)

    # Add default variables
    stack.parse.add_required(key="topic_name",
                             tags="tfvar",
                             types="str")
    
    stack.parse.add_required(key="lambda_name",
                             tags="tfvar",
                             types="str")

    stack.parse.add_optional(key="aws_default_region",
                             default="eu-west-1",
                             tags="tfvar,resource,db,tf_exec_env",
                             types="str")

    # Add execgroup
    stack.add_execgroup("config0-publish:::aws::codebuild_evntbrdg_sns_lambda",
                        "tf_execgroup")

    # Add substack
    stack.add_substack('config0-publish:::tf_executor')

    # Initialize Variables in stack
    stack.init_variables()
    stack.init_execgroups()
    stack.init_substacks()

    tf = TFConstructor(stack=stack,
                       provider="aws",
                       execgroup_name=stack.tf_execgroup.name,
                       resource_name=stack.topic_name,
                       resource_type="sns_topic_subscription")

    tf.include(values={
        "aws_default_region":stack.aws_default_region,
        "topic_name":stack.topic_name,
    })

    tf.output(keys=["id",
                    "topic_arn",
                    "endpoint"])

    # finalize the tf_executor
    stack.tf_executor.insert(display=True,
                             **tf.get())

    return stack.get_results()
