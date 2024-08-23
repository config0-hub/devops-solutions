**Description**

This stack combines networking related stacks.

  - stack that combines
    + vpc
    + network variables set
    + nat instance
     
**Required**
| argument       | description                            | var type | default      |
| -------------- | -------------------------------------- | -------- | ------------ |

**Optional**

| argument            | description                                        | var type | default   |
| ------------------- | -------------------------------------------------- | -------- | --------- |
| aws_default_region  | default aws region                                 |string    | eu-west-1 |
| cloud_tags_hash     | the tags for the resources in the cloud as base64  |string    | None |

