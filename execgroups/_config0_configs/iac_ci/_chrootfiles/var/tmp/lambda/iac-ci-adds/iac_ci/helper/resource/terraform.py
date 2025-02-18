#!/usr/bin/env python

import os

from iac_ci.helper.resource.tfinstaller import get_tf_install
from iac_ci.helper.resource.common import TFAppHelper

class TFCmdOnAWS(TFAppHelper):
    """
    Class for managing Terraform commands execution on AWS.
    Provides methods for Terraform operations including init, plan, apply, and destroy.
    Inherits from TFAppHelper.
    """

    def __init__(self,**kwargs):
        """
        Initialize TFCmdOnAWS with AWS-specific configurations.

        Args:
            **kwargs: Keyword arguments including:
                app_dir (str): Application directory path
                envfile (str): Environment file name
                tf_bucket_path (str): Terraform bucket path
                run_share_dir (str): Shared directory path
                binary (str): Binary name
                version (str): Version number
                arch (str): Architecture type
                runtime_env (str): Runtime environment
        """
        self.classname = "TFCmdOnAWS"

        self.app_name = "terraform"
        self.app_dir = kwargs["app_dir"]  # e.g. var/tmp/terraform
        self.envfile = kwargs["envfile"]  # e.g. build_env_vars.env
        self.tf_bucket_path = kwargs["tf_bucket_path"]
        self.run_share_dir = kwargs["run_share_dir"]
        self.ssm_tmp_dir = "/tmp"

        TFAppHelper.__init__(self,
                             binary=kwargs["binary"],
                             app_dir=self.app_dir,
                             version=kwargs["version"],
                             arch=kwargs["arch"],
                             runtime_env=kwargs["runtime_env"])

    def get_tf_install(self):
        """
        Get Terraform installation commands.

        Returns:
            list: Commands for installing Terraform
        """
        return get_tf_install(
                runtime_env=self.runtime_env,
                binary=self.binary,
                version=self.version,
                tf_bucket_path=self.tf_bucket_path,
                arch=self.arch,
                bin_dir=self.bin_dir)

    @staticmethod
    def _get_ssm_concat_cmds():
        """
        Get commands for concatenating SSM parameters.
        Used only for CodeBuild.

        Returns:
            list: Commands for SSM parameter handling
        """
        return (
            [
                'echo $SSM_VALUE | base64 -d >> $TMPDIR/.ssm_value && cat $TMPDIR/.ssm_value'
            ]
            if os.environ.get("DEBUG_STATEFUL")
            else ['echo $SSM_VALUE | base64 -d >> $TMPDIR/.ssm_value']
        )

    def _set_src_envfiles_cmd(self):
        """
        Set commands for environment file setup.
        Used only for CodeBuild.

        Returns:
            list: Commands for environment file setup
        """
        exclude_var_cmd = '''export $(awk -F= '!/^#/ && !($1 in ENVIRON) {print $1 "=" $2}' .env)'''
        ssm_cmd = 'if [ -f $TMPDIR/.ssm_value ]; then cd $TMPDIR/; . ./.ssm_value; fi'

        return [
            f'if [ -f {self.stateful_dir}/{self.envfile}; then mv {self.stateful_dir}/{self.envfile} /tmp/.env; fi',
            f'if [ -f /tmp; then cd /tmp && {exclude_var_cmd}; fi',
            ssm_cmd,
        ]

    def load_env_files(self):
        """
        Load environment files and SSM parameters.

        Returns:
            list: Commands for loading environment files
        """
        envfile = os.path.join(self.app_dir, self.envfile)

        cmds = [
            f'rm -rf {self.stateful_dir}/{envfile} > /dev/null 2>&1 || echo "env file already removed"',
            f'if [ -f {self.stateful_dir}/run/{envfile}.enc ]; then cat {self.stateful_dir}/run/{envfile}.enc | base64 -d > {self.stateful_dir}/{self.envfile}; fi'
        ]

        # TODO - will we need SSM_NAMES plural?
        cmds.extend(self._get_ssm_concat_cmds())
        cmds.extend(self._set_src_envfiles_cmd())
        return cmds

    def s3_tfpkg_to_local(self):
        """
        Copy Terraform package from S3 to local filesystem.

        Returns:
            list: Commands for copying and extracting Terraform package
        """
        cmds = self.reset_dirs()

        # ref 4353253452354
        cmds.extend([
            'echo "remote bucket s3://$REMOTE_SRC_BUCKET/$REMOTE_SRC_BUCKET_KEY"',
            f'aws s3 cp s3://$REMOTE_SRC_BUCKET/$REMOTE_SRC_BUCKET_KEY {self.stateful_dir}/src.$STATEFUL_ID.zip --quiet',
            f'rm -rf {self.stateful_dir}/run > /dev/null 2>&1 || echo "stateful already removed"',
            f'unzip -o {self.stateful_dir}/src.$STATEFUL_ID.zip -d {self.stateful_dir}/run',
            f'rm -rf {self.stateful_dir}/src.$STATEFUL_ID.zip'
        ])
        return cmds

    def _get_tf_validate(self):
        """Get Terraform validation commands"""
        suffix_cmd = f'{self.base_cmd} validate -no-color 2>&1 | tee {self.tmp_base_output_file}.validate'
        cmds = [ f'{suffix_cmd}' ]
        cmds.extend(self.local_output_to_s3(suffix="validate",last_apply=None))
        return cmds

    def _get_tf_init(self):
        """Get Terraform initialization commands"""
        suffix_cmd = f'{self.base_cmd} init -no-color 2>&1 | tee {self.tmp_base_output_file}.init'
        cmds = [f'{suffix_cmd} || (rm -rf .terraform && {suffix_cmd})']
        cmds.extend(self.local_output_to_s3(suffix="init",last_apply=None))
        return cmds

    def _get_tf_plan(self):
        """Get Terraform plan commands"""
        cmds = [
            f'{self.base_cmd} plan -out={self.tmp_base_output_file}.tfplan',
            f'{self.base_cmd} show -no-color {self.tmp_base_output_file}.tfplan > {self.tmp_base_output_file}.tfplan.out',
            f'{self.base_cmd} show -no-color -json {self.tmp_base_output_file}.tfplan > {self.tmp_base_output_file}.tfplan.json'
        ]
        cmds.extend(self.local_output_to_s3(suffix="tfplan",last_apply=None))
        cmds.extend(self.local_output_to_s3(suffix="tfplan.json",last_apply=None))
        cmds.extend(self.local_output_to_s3(suffix="tfplan.out",last_apply=None))
        return cmds

    def get_tf_ci(self):
        """Get commands for CI pipeline"""
        cmds = self._get_tf_init()
        cmds.extend(self._get_tf_validate())
        cmds.extend(self.get_tf_chk_fmt(exit_on_error=True))
        cmds.extend(self._get_tf_plan())
        return cmds

    def get_tf_pre_create(self):
        """Get commands for pre-creation phase"""
        cmds = self._get_tf_init()
        cmds.extend(self._get_tf_validate())
        cmds.extend(self._get_tf_plan())
        return cmds

    def get_tf_apply(self,destroy_on_failure=None):
        """
        Get commands for applying Terraform configuration.

        Args:
            destroy_on_failure (bool): Whether to destroy resources on failure

        Returns:
            list: Commands for applying Terraform configuration
        """
        cmds = self._get_tf_init()
        cmds.extend(self._get_tf_validate())
        cmds.extend(self.s3_file_to_local(suffix="tfplan", last_apply=None))

        if destroy_on_failure:
            cmds.append(f"({self.base_cmd} apply {self.base_output_file}.tfplan) || ({self.base_cmd} destroy -auto-approve && exit 9)")
        else:
            cmds.append(f"({self.base_cmd} apply {self.base_output_file}.tfplan)")

        return cmds

    def get_tf_destroy(self):
        """Get commands for destroying Terraform resources"""
        cmds = self._get_tf_init()
        cmds.append(f'{self.base_cmd} destroy -auto-approve')
        return cmds

    def get_tf_chk_fmt(self,exit_on_error=True):
        """
        Get commands for checking Terraform formatting.

        Args:
            exit_on_error (bool): Whether to exit on formatting errors

        Returns:
            list: Commands for checking formatting
        """
        if exit_on_error:
            cmd = f'{self.base_cmd} fmt -no-color -check -recursive 2>&1 | tee {self.tmp_base_output_file}.fmt'
        else:
            cmd = f'{self.base_cmd} fmt -no-color -write=false -recursive 2>&1 | tee {self.tmp_base_output_file}.fmt'

        cmds = [cmd]
        cmds.extend(self.local_output_to_s3(suffix="fmt",last_apply=None))
        return cmds

    def get_tf_chk_drift(self):
        """Get commands for checking infrastructure drift"""
        cmds = self._get_tf_init()
        cmds.extend([
            f'({self.base_cmd} refresh',
            f'({self.base_cmd} plan -detailed-exitcode'
        ])
        return cmds
