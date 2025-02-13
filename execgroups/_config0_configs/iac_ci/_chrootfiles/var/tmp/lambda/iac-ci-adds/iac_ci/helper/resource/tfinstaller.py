#!/usr/bin/env python

def get_tf_install(**kwargs):
    """
    Generate commands for installing Terraform or OpenTofu from either S3 cache or source.
    
    This function creates a series of shell commands to:
    1. Attempt to download the binary from an S3 bucket cache
    2. If cache miss, download from official sources (HashiCorp or OpenTofu GitHub)
    3. Install the binary in the specified directory
    
    Args:
        **kwargs: Keyword arguments including:
            runtime_env (str): Runtime environment ('codebuild' or 'lambda')
            binary (str): Binary name ('terraform' or 'opentofu')
            version (str): Version of the binary to install
            bucket_path (str): S3 bucket path for caching
            arch (str): Architecture (e.g., 'linux_amd64')
            bin_dir (str): Directory to install the binary
    
    Returns:
        list: Shell commands for downloading and installing the binary
    
    Example URLs:
        Terraform: https://releases.hashicorp.com/terraform/x.y.z/terraform_x.y.z_linux_amd64.zip
        OpenTofu: https://github.com/opentofu/opentofu/releases/download/vx.y.z/tofu_x.y.z_linux_amd64.zip
    """
    runtime_env = kwargs["runtime_env"]
    binary = kwargs["binary"]
    version = kwargs["version"]
    bucket_path = kwargs["tf_bucket_path"]
    arch = kwargs["arch"]
    bin_dir = kwargs["bin_dir"]

    _hash_delimiter = f'echo "{"#" * 32}"'

    # Commands for downloading from S3 cache
    _bucket_install_1 = f'aws s3 cp {bucket_path} $TMPDIR/{binary}_{version} --quiet'
    _bucket_install_2 = f'echo "# GOT {binary} from s3/cache"'
    bucket_install = f'{_bucket_install_1} && {_hash_delimiter} && {_bucket_install_2} && {_hash_delimiter}'

    # Common commands for direct download
    _terraform_direct_1 = f'echo "# NEED {binary}_{version} FROM SOURCE"'
    _terraform_direct_3 = f'aws s3 cp {binary}_{version} {bucket_path} --quiet'

    # Terraform-specific download command
    _terraform_direct_2 = f'cd $TMPDIR && curl -L -s https://releases.hashicorp.com/terraform/{version}/{binary}_{version}_{arch}.zip -o {binary}_{version}'
    terraform_direct = f'{_hash_delimiter} && {_terraform_direct_1} && {_hash_delimiter} && {_terraform_direct_2} && {_terraform_direct_3}'

    # OpenTofu-specific download command
    _tofu_direct_2 = f'cd $TMPDIR && curl -L -s https://github.com/opentofu/opentofu/releases/download/v{version}/{binary}_{version}_{arch}.zip -o {binary}_{version}'
    tofu_direct = f'{_hash_delimiter} && {_terraform_direct_1} && {_hash_delimiter} && {_tofu_direct_2} && {_terraform_direct_3}'

    # Choose appropriate installation command based on binary type
    if binary == "terraform":
        _install_cmd = f'({bucket_install} )|| (echo "terraform/tofu not found in local s3 bucket" && {terraform_direct})'
    else:  # opentofu
        _install_cmd = f'({bucket_install}) || (echo "terraform/tofu not found in local s3 bucket" && {tofu_direct})'

    return [
        _install_cmd,
        *[
            f'mkdir -p {bin_dir} || echo "trouble making bin_dir {bin_dir}"',
            f'(cd $TMPDIR && unzip {binary}_{version} && mv {binary} {bin_dir}/{binary} > /dev/null) || exit 0',
            f'chmod 777 {bin_dir}/{binary}',
        ],
    ]
