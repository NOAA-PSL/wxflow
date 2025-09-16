from typing import List, Union
import os
import tarfile
import glob
from logging import getLogger
from pathlib import Path

from .executable import which
from .fsutils import get_gid, rmdir, mkdir_p
from .file_utils import FileHandler 
from .logger import logit

__all__ = ['Aws']

logger = getLogger(__name__.split('.')[-1])

class Aws:
    """
    
    Class offering an interface to Aws via the aws utility.  This class is meant to reflect
    the functionality of both hsi.py and htar.py, but in the Aws domain rather than HPSS.
    Question: should this have the htar functionality as well?  Need to see if Aws allows in-bucket archiving.
    
    Examples:
    --------
    
    >>>> from wxflow import Aws
    >>>> aws = Aws() # Generates an Executable object of "aws"
    >>>> output = aws.put("some_local_file", "/Aws/path/to/some_file") # Put a file onto Aws
    >>>> output = aws.ls("Aws/path/to/some_file") # List the file
    """
    
    # TODO: figure out how error codes work in hsi
    
    def __init__(self, quiet: bool = False, echo_commands: bool = True, opts: Union[str, List] = []):
        """Instantiate the aws command
        
        Parameters:
        -----------
        quiet : bool
                Run aws in quiet mode (suppress login info, transfer info, etc)
        echo_commands : bool
                Echo each command
        opts : str | list
                Additional arguments to send to each aws command
        """
        
        self.exe = which("aws", required=True)
        
        aws_args = []
        
        aws_args.append("s3")
        
        #aws_args.append("--profile=globalarchive")
        
        #if quiet:
        #    aws_args.append("--quiet")
            
        #if echo_commands:
        #    aws_args.append("-e")
            
        #aws_args.extend(Aws._split_opts(opts))
        
        for arg in aws_args:
            self.exe.add_default_arg(arg)

        
    def _aws(self, arg_list: list, silent: bool = False, ignore_errors: list = []) -> str:
        """Direct command builder function for aws based on the input arguments
        
        Parameters:
        -----------
        arg_list : list
                A list of arguments to send to aws
                
        silent : bool
                Whether the output of the aws command should be written to stdout
                
        ignore_errors : list
                List of error numbers to ignore.
                
        Returns
        -------
        output : str
                Concatenated otuput and error of the aws command
        
        Example:
        --------
            >>>> aws = Aws()
            >>>> # Execute `aws get some_local_file : /some/aws/file`
            >>>> aws._aws(["get","some_local_file : /some/aws/file"])
        """
        
        # Remove any empty arguments in case they cause issues for aws
        arg_list = [arg for arg in arg_list if arg != ""]
        
        if silent:
            output = self.exe(*arg_list, output=str, error=str, ignore_errors=ignore_errors)
            
        else:
            output = self.exe(*arg_list, output=str.split, error=str.split, ignore_errors=ignore_errors)
            
        return output
        
    def get(self, source: str, target=None, opts: Union[List, str] = []) -> str:
        """ Method to get a file from aws
        
        Parameters:
        ----------
        source : str
                Full path location on Aws of the file.  This must be of the form "s3://<bucket>/<key>" or "s3://<access-point-arn>/<key>"
        
        target: str
                Local location to place the file. If not specified, places file in current directory
                
        opts : str | list
                List or string of additional options to send to aws command
                
        Returns:
        --------
        output : str
                Concatenated output and error of aws command
        """
        arg_list = []
        
        # Convert to str to handle Path objects
        source = str(source)
        target = str(target) if target is not None else None
        
        arg_list.append("cp")
        arg_list.append(source)
        if target is not None:
            arg_list.append(target)
        
        # Specify which credentials profile to use
        arg_list.append("--profile=globalarchive")

        # Parse any aws options
        arg_list.extend(Aws._split_opts(opts))

        output = self._aws(arg_list)
        
        return output
        
    def put(self, source: str, target: str, opts: Union[List, str] = [],
            listing_file: str = None) -> str:
        """ Method to put a file onto Aws
        
        Parameters:
        -----------
        source : str
                Location on the local machine of the source file to send to Aws
                
        target : str
                Full path of the target location of the file in Aws.  This must be of the form "s3://<bucket>/<key>" or "s3://<access-point-arn>/<key>"
                
        opts : str | List
                List or string of additional options to send to Aws
        
        Returns:
        --------
        output : str
                Concatenated output and error of the put command
        """        
        arg_list = []
        
        # Convert to str to handle Path objects
        target = str(target)
        source = str(source)
        
        arg_list.append("cp")
        arg_list.append(source)
        arg_list.append(target)
        
        # Specify which credentials profile to use
        arg_list.append("--profile=globalarchive")

        # Parse Aws options
        arg_list.extend(Aws._split_opts(opts))

        output = self._aws(arg_list)

        return output
        
    # OMIT:
    # def chmod(self, mod: str, target: str, aws_opts: Union[List, str] = "",
    #           chmod_opts: Union[List, str] = "") -> str:
    #  this is unnecessary as permissions are not preserved when copying to AWS
    
    
    # OMIT:
    # def chgrp(self, group_name: str, target: str, aws_opts: str = "",
    #           chgrp_opts: str = "") -> str:
    #  this is unnecessary as permissions are not preserved when copying to AWS
    
    def rm(self, target: str, recursive: bool = False, aws_opts: str = "", rm_opts: str = "") -> str:
        """ Method to delete a file or directory on Aws
        
        Parameters
        ----------
        target : str
                Full path of the target location of the file in Aws bucket.
                This must be of the form "s3://<bucket>/<key>" or "s3://<access-point-arn>/<key>"
                
        aws_opts: str
                String of Aws options
        
        rm_opts : str
                Options to send to rm.
        
        recursive : bool
                Flag to delete a directory with contents
        
        Returns
        -------
        output : str
                Concatenated output and error of the aws rm command
        """
        
        arg_list = []
        
        
        arg_list.append("rm")
        
        # Parse rm options
        arg_list.extend(Aws._split_opts(rm_opts))
        
        arg_list.append(target)

        if recursive:
            arg_list.append("--recursive")

        # Parse aws options
        arg_list.extend(Aws._split_opts(aws_opts))

        # Parse rm options
        arg_list.extend(Aws._split_opts(rm_opts))

        output = self._aws(arg_list)
        
        return output
        
    # OMIT:
    # def rmdir
    #   this functionality is handled by the "recursive" flag in rm above
    
    
    # OMIT:
    # def mkdir
    #   this functionality is undefined in aws cli but also unnecessary, as the s3 cp command will create parent directories as needed based on the specified target path
    
    def ls(self, target: str, aws_opts: str = "", ls_opts: str = "",
            ignore_missing: bool = False) -> str:
        """ Method to list files/directories in AWS bucket
        
        Parameters
        ----------
        target : str
                Full path of the target location on AWS.
                
        aws_opts : str
                String of options to send to aws
        
        ls_opts : str
                String of options to send to ls
                
        ignore_missing : bool
                Flag to ignore missing files
        
        Returns
        -------
        output : str
                Concatenated output and error of the aws ls command
        """
        
        arg_list = []
        
        arg_list.append("ls")

        arg_list.append(target)

        # Specify which credentials profile to use
        arg_list.append("--profile=globalarchive")

        # Parse aws options
        arg_list.extend(Aws._split_opts(aws_opts))
        
        # Parse ls options
        arg_list.extend(Aws._split_opts(ls_opts))
        
        output = self._aws(arg_list)
        
        return output
        
    def exists(self, target: str) -> bool:
        """ Method to test existence of file/directory on Aws
        
        Parameters
        ----------
        target : str
                Full path of the target location on Aws
                
        Returns
        -------
        pattern_exists : bool
                True iff the target exists on Aws in specified bucket/location
        
        """
        
        arg_list = ["-q", "ls", target]
        
        # Do not exit if the file is not found, do not pipe output to stdout
        output = self._aws(arg_list, silent=True)
        
        # TODO: handle return from Aws
        # the existing code in hsi.py works for hsi
        
        pattern_exists = False
        
        return pattern_exists
        
    def cvf(self, target: str, fileset: Union[List, str], dereference: bool = False) -> str:
        """ Method to write an archive to AWS.
        
        Parameters
        ----------
        target : str
                Full path location on AWS to create the archive.
        
        fileset : List | str
                List containing filenames, patterns, or directories to archive.
        
        dereference : bool
                Whether to dereference symbolic links (archive the pointed-to files instead).
                
        Returns
        -------
        output : str
                Concatenated output and error from the htar command
        """
        
        output = self.create(target, fileset, dereference)
        
        return output
    
    @logit(logger)
    def create(self, target: str, fileset: Union[List, str],
               dereference: bool = False, opts: Union[List, str] = []) -> str:
        """ Method to write an archive to AWS
        
        Parameters
        ----------
        opts : str | list
                Options to send to AWS.  Archiving directories will not work without a --recursive flag.
                
        target : str
                Full path location on AWS to create the archive.
                
        fileset : List | str
                List containing filenames, patterns, or directories to archive.
                
        dereference : bool
                Whether to dereference symbolic links (archive the pointed-to files instead).
        
        Returns
        -------
        output : str
                Concatenated otuput and error of the aws command
        """        
        
        # Don't actually tar - individual files need to be accessible from the bucket
        
        if len(fileset) == 0:
            raise ValueError("Input fileset is empty, nothing to archive")

        output = ""

        if dereference:
            opts.append("--follow-symlinks")
        else:
            opts.append("--no-follow-symlinks")

        try:
            rstprod_gid = get_gid("rstprod")
        except KeyError:
            rstprod_gid = -1;

        # can't use pathlib here, as the s3 link will not resolve correctly as a path, and python will jam the current working dir onto the front of the path
        parent_target = target.rpartition("/")[0] + target.rpartition("/")[1]
        target_tarname = target.rpartition("/")[2]
        target_name = target_tarname.replace(".", "")
        target_name_archive = "tmp_archive_" + target_name

        filelist = []
        rotdir = os.environ.get("ROTDIR")    # normally we'd pull this from the arch_dict, but it doesn't exist at this scope
        temp_target = os.path.join(rotdir, target_name_archive)
        temp_target += "/"
        if not os.path.isdir(temp_target):
            mkdir_p(temp_target)

        for file_or_glob in Aws._split_opts(fileset):
            glob_set = glob.glob(file_or_glob)
            for filename in glob_set:
                if os.stat(filename).st_gid == rstprod_gid:
                    logger.warning(f"WARNING: skipping rst_prod file {filename} as it cannot have protected access on AWS.")
                else:
                    targetpath = os.path.join(temp_target, filename)
                    if not os.path.isdir(Path(targetpath).parent.resolve()):
                        mkdir_p(Path(targetpath).parent.resolve())
                    sublist = [filename, targetpath]
                    filelist.append(sublist)
        
        FileHandler({'copy': filelist}).sync()
        opts.append("--recursive")
        output = self.put(temp_target, parent_target, opts)

        rmdir(temp_target)
        
        return output

        
    @staticmethod
    def _split_opts(opts: Union[List, str] = "") -> list:
        """ Method to split intput list or string or options
        
        Parameters
        ----------
        opts : list | str
                Input list or string of options to send to aws or subcommand
                
        Returns
        -------
        split_opts : list
                List of options to send to aws or subcommand
        """
        
        split_opts = opts.split(" ") if isinstance(opts, str) else opts
        
        return split_opts
        
    
