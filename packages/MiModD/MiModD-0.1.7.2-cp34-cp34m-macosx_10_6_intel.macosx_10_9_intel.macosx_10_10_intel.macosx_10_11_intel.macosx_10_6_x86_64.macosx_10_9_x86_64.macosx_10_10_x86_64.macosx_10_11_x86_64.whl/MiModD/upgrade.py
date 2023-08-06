import sys
import os
import shutil
import fnmatch
import tempfile
import argparse
from io import StringIO

import pip

from . import config, __version__


MAIN_REPO = 'http://hg.code.sf.net/p/mimodd/source'


class MiModDInstallationError (Exception):
    pass


def find_executable(executable='mimodd', path=None, flags=os.X_OK):
    """Find the mimodd executable in the directories listed in 'path'.
 
    A string listing directories separated by 'os.pathsep'; defaults to
    os.environ['PATH'].  Returns the complete filename or None if not found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
     
    if not os.path.isfile(executable):
        for p in paths:
            f = os.path.join(p, executable)
            if os.access(f, flags):
                return f
        return None
    else:
        return executable


def main (mode = None, version = None, **args):
    global __version__
    # Logic of following argument parsing:
    # When used without args: run 'pip search MiModD' and display output.
    # When used with 'install' or 'hg-install' subcommand
    # and a specific version:
    # use 'pip install MiModD==version' or
    # 'pip install hg+MAIN_REPO@version#egg=MiModD'
    # to install that specific version.
    # For 'install' a check is performed first to see if the
    # user-provided version string is valid.
    # If no version is given, then for hg-install:
    # use 'pip install hg+MAIN_REPO#egg=MiModD'
    # to install the repository tip, but for install:
    # use 'pip install 'MiModD>current_version''
    # i.e., run upgrade only if a newer version than the currently
    # installed one is available.
    # Summary:
    # No restrictions apply when using hg-install, use at your own risk!
    # However, prevent the most annoying mistakes in install mode.
    if not mode:
        if not args.get('from_file'):
            print('Checking for latest available version ...')
            old_stdout = sys.stdout
            try:
                sys.stdout = buffer = StringIO()
                pip.main(['search', 'MiModD'])
            finally:
                sys.stdout = old_stdout
                print(buffer.getvalue())
    else:
        pip_args = args['pip_args']
        new_version = None
        if mode == 'install':
            
            if args.get('from_file'):
                # ugly hack to allow upgrading to local test versions
                version = None
                __version__ = '0.0.1'
                pip_args[1] = args['from_file']

            if version:
                # Prevent downgrading beyond v0.1.5.3 when upgrading was
                # introduced.
                try:
                    new_version = tuple(int(d) for d in version.split('.'))
                except:
                    print('Invalid version number.')
                    sys.exit(1)
                if new_version < (0, 1, 5, 3):
                    print('Cannot downgrade to versions older than 0.1.5.3')
                    sys.exit(1)
                pip_args[1] = pip_args[1].format(
                    args['version_separator'] + version
                    )
            else:
                pip_args[1] = pip_args[1].format('>'+str(__version__))
        else:
            if version:
                pip_args[1] = pip_args[1].format(
                    repo=args.get('repo', MAIN_REPO),
                    changeset=args['version_separator'] + version
                    )
            else:
                pip_args[1] = pip_args[1].format(
                    repo=args.get('repo', MAIN_REPO),
                    changeset=''
                    )

                
        warn_count = 0
        migrate_these = ['cfg.py']
        # the following get migrated only during an explicit downgrade to
        # an *older release* version (never during hg-installs)
        backport_these = ['.__first_run__']

        current_package_dir = os.path.dirname(__file__)
        current_install_dir = os.path.dirname(current_package_dir)
        # check that we have write permissions in the current
        # installation directory. This check may be misleading since
        # it does not prove that we can delete things not owned by us,
        # but it is good enough in most cases.
        try:
            try:
                with tempfile.TemporaryFile(dir=current_install_dir):
                    pass
            except (IOError, OSError) as e:
                if e.errno == 13:
                    raise MiModDInstallationError(
                        'You do not seem to have permission to modify the current installation. Maybe you need to use "sudo"?'
                        )
                else:
                    raise
            with tempfile.TemporaryDirectory(
                 prefix='MiModDinstall',
                 dir=config.tmpfile_dir) as temp_install_dir:
                temp_package_dir = os.path.join(temp_install_dir, 'MiModD')

                # pip install to temporary installation directory
                pip_args += ['--target', temp_install_dir]
                retcode = pip.main(pip_args)
                if retcode:
                    raise MiModDInstallationError(
                        'Installation error. Upgrade aborted')
                
                # migrate files to temporary package directory
                for f in migrate_these:
                    src = os.path.join(current_package_dir, f)
                    dst = os.path.join(temp_package_dir, f)
                    if os.path.isfile(src):
                        shutil.copyfile(src, dst)
                if new_version is not None and new_version < __version__:
                    for f in backport_these:
                        src = os.path.join(current_package_dir, f)
                        dst = os.path.join(temp_package_dir, f)
                        if os.path.isfile(src):
                            shutil.copyfile(src, dst)

                # replace current package directory with temporary one
                try:
                    shutil.rmtree(current_package_dir)
                except (IOError, OSError):
                    raise MiModDInstallationError(
                        'Cannot remove the current installation. Upgrade aborted'
                        )
                for d in os.listdir(current_install_dir):
                    p = os.path.join(current_install_dir, d)
                    if os.path.isdir(p) and fnmatch.fnmatch(d, 'MiModD-*-info'):
                        try:
                            shutil.rmtree(p)
                        except (IOError, OSError):
                            print("""
WARNING: Failed to remove old installation info: {}.
Future runs of MiModD.upgrade may report a wrong installed version."""
                                  .format(d))
                            warn_count += 1
                for d in os.listdir(temp_install_dir):
                    src = os.path.join(temp_install_dir, d)
                    dst = os.path.join(current_install_dir, d)
                    if not os.path.exists(dst):
                        shutil.copytree(src, dst)

            try:
                # If .__first_run__ exists, this is a downgrade situation
                # and the file got backported from a version >= v0.1.7.2.
                # In this situation, we want to overwrite a possibly
                # preexisting __first_run__.py.
                shutil.copyfile(os.path.join(current_package_dir,
                                             '.__first_run__'),
                                os.path.join(current_package_dir,
                                             '__first_run__.py')
                                )
            except (IOError, OSError):
                # If there is no .__first_run__, that is ok.
                # We will try to see if there is a __first_run__ module
                # provided by the version upgraded to.
                pass
            finally:
                try:
                    os.remove(os.path.join(current_package_dir,
                                           '.__first_run__')
                              )
                except:
                    pass
            try:
                from . import __first_run__
                first_run_script = True
            except ImportError:
                # could not get code for first run
                # minimal configuration of the fresh installation will have
                # to be done by the upgrade tool
                first_run_script = False
                raise

            if first_run_script:
                try:
                    __first_run__.prepare_package_files()
                except:
                    print("""
Warning:
Problems were encountered during configuration of the upgraded package.
If the upgraded package does not continue to function properly, your best
option may be to try a clean install of the package.
Since this will discard your current configuration settings, you may want
to copy your current configuration settings shown on the following lines:""")
                    config.display_config(title='')
                    _ = input('After copying your old settings above press Enter to see the complete exception traceback.')
                    raise
            else:
                # minimal configuration for legacy versions in the absence
                # of a __first_run__ module:
                # run enablegalaxy and check if bin/mimodd exists
                try:
                    from . import enablegalaxy
                    enablegalaxy.GalaxyAccess.set_toolbox_path()
                except:
                    print("""
WARNING: Failed to migrate your Galaxy settings.
If you want to use your installation of MiModD with Galaxy, you will have to
run "python3 -m MiModD.enablegalaxy" to activate Galaxy support even if you
have already done so for your old installation.""")
                    warn_count += 1

                # verify that this build  has a copy of the mimodd executable
                # in its bin directory and emit a warning if it does not
                package_executable = os.path.join(current_package_dir,
                                                  'bin', 'mimodd')
                if not os.path.isfile(package_executable):
                    print("""
This version does not seem to have the expected executable copy at {0}.
You will have to download the latest executable separately to make sure you have the latest version.""")
                    warn_count += 1
        except MiModDInstallationError as e:
            print(e.args[0])
            sys.exit(1)

        print()
        print('Upgrade completed! {} problem(s) encountered.'
              .format(warn_count or 'No'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
             usage=argparse.SUPPRESS,
             formatter_class=argparse.RawDescriptionHelpFormatter,
             description = """

standard usage:

  MiModD.upgrade install     to upgrade to the latest available version
  
""")
    subparsers = parser.add_subparsers(title='available actions', metavar='')
    # upgrade install command
    p_install = subparsers.add_parser('install',
                help='upgrade your MiModD installation to a different release')
    p_install.add_argument('-v', '--version', default=argparse.SUPPRESS,
                help='the release number to upgrade to (default: latest)')
    p_install.set_defaults(pip_args=['install', 'MiModD{0}'],
                           version_separator='==',
                           mode='install')
    # upgrade hg-install command
    p_hg_install = subparsers.add_parser('hg-install',
                help='upgrade to an unstable in-development version (NOT recommended for standard users)')
    p_hg_install.add_argument('-v', '--version', default=argparse.SUPPRESS, metavar='CHANGESET', help='the specific changeset to upgrade to (default: tip)')
    p_hg_install.set_defaults(pip_args=['install',
                                        'hg+{repo}{changeset}#egg=MiModD'],
                              version_separator='@',
                              mode='hg-install')

    main(**vars(parser.parse_args()))
