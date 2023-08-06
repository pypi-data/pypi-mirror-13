import sys
import os
import shutil
import shlex

import xml.etree.ElementTree as ET


INTERPRETER_EXECUTABLE = sys.executable
CURRENT_PACKAGE_DIR, fn = os.path.split(__file__)


# remove ourselves
# remember: from version 0.1.7.2 onwards
# there is always a copy of this module named .__first_run__
os.remove(__file__)


from . import enablegalaxy


def configure (args, config):
    """Interactive package configuration after fresh install."""

    fix_executable_shebang()
    prepare_galaxy_integration()
    
    if not 'tmpfiles_path' in args:
        choice = input(
            'Which folder should MiModD use to store temporary data? [{0}]:'
            .format(config.tmpfiles_path))
        if choice:
            args['tmpfiles_path'] = choice
    if not 'snpeff_path' in args:
        choice = input(
            'In which folder should MiModD look for SnpEff? [{0}]:'
            .format(config.snpeff_path))
        if choice:
            args['snpeff_path'] = choice
    if not 'multithreading_level' in args:
        choice = input(
            'Up to how many threads do you want to allow MiModD to use at a time? [{0}]:'
            .format(config.multithreading_level))
        if choice:
            args['multithreading_level'] = choice
    if not 'max_memory' in args:
        choice = input(
            'Up to how much memory in GB do you want to allow MiModD to use? [{0}]:'
            .format(config.max_memory))
        if choice:
            args['max_memory'] = choice
    print("""
All necessary information has been collected. Hit <Enter> to store your settings and start using MiModD.

To change settings later, you can rerun this tool with new settings provided as command line options.

""")
    _ = input()


def prepare_package_files ():
    """Automatic package configuration during upgrade."""

    print('Configuring newly installed files ...', end=' ')
    sys.stdout.flush()

    errors = False
    try:
        fix_executable_shebang()
    except:
        errors = True
        raise
    finally:
        try:
            prepare_galaxy_integration()
        except:
            errors = True
            raise
        finally:
            print('FAILED' if errors else 'done')

            print('Migrating settings ...', end=' ')
            try:    
                upgrade_cfg()
                print('done')
            except:
                print('FAILED')
                raise
            

def upgrade_cfg ():
    cfg_current = os.path.join(CURRENT_PACKAGE_DIR, 'cfg.py')
    cfg_template = os.path.join(CURRENT_PACKAGE_DIR, '.cfg')
    if not os.path.isfile(cfg_template):
        template_settings = [i + '\n' for i in DEFAULTCONFIG.split('\n')]
    else:
        with open(cfg_template, 'r', encoding='utf-8') as template:
            template_settings = template.readlines()
    with open(cfg_current, 'r', encoding='utf-8') as current:
        current_backup = current.readlines()

    current_settings = {}
    for line in current_backup:
        if line.strip() and line.lstrip()[0] != '#':
            key, value = [part.strip() for part in line.split('=')]
            current_settings[key] = value

    newcfg_lines = []            
    for line in template_settings:
        overwrite = False
        if not line.strip() or line.lstrip()[0] == '#':
            newcfg_lines.append(line)
            continue
        if line[0] == '!':
            line = line[1:]
            overwrite = True
        key, value = [part.strip() for part in line.split('=')]
        if overwrite or key not in current_settings:
            newcfg_lines.append(line)
        else:
            newcfg_lines.append('{0}= {1}\n'
                                .format(line.split('=')[0],
                                        current_settings[key])
                                )
            
    with open(cfg_current, 'w', encoding='utf-8') as newcfg:
        try:
            newcfg.writelines(newcfg_lines)
        except:
            newcfg.close()
            with open(cfg_current, 'w', encoding='utf-8') as newcfg:
                newcfg.writelines(current_backup)
            raise


def fix_executable_shebang ():
    scripts_dir = os.path.join(CURRENT_PACKAGE_DIR, 'bin')
    # Adjust the shebang line to the environment if possible.
    if INTERPRETER_EXECUTABLE and not ' ' in INTERPRETER_EXECUTABLE:
        # with POSIX systems there is no way to form a valid shebang line
        # if there is a space in the executable path so we leave the file alone.
        # Under Windows we could do:
        # if ' ' in interpreter_executable:
        #    # quote the interpreter path if it contains spaces
        #    interpreter_executable = '"%s"' % interpreter_executable

        with open(os.path.join(scripts_dir, 'mimodd'),
                  'r', encoding='utf-8') as script_in:
            first_line = script_in.readline()
            if not first_line.startswith('#!'):
                raise RuntimeError(
                    'Compromised starter script.'
                    )
            first_line = '#!' + INTERPRETER_EXECUTABLE + '\n'
            remaining_lines = script_in.readlines()
        with open(os.path.join(scripts_dir, 'mimodd'),
                  'w', encoding='utf-8') as script_out:
            script_out.write(first_line)
            script_out.writelines(remaining_lines)


def prepare_galaxy_integration ():
    tool_wrapper_dir = os.path.join(CURRENT_PACKAGE_DIR,
                                    'galaxy_data',
                                    'mimodd')
    enablegalaxy.GalaxyAccess.set_toolbox_path()
    if INTERPRETER_EXECUTABLE:
        try:
            interpreter_executable = shlex.quote(INTERPRETER_EXECUTABLE)
        except AttributeError:
            # shlex.quote is available from Python 3.3 onwards
            # without it, we play it save and add surrounding quotes in any case
            interpreter_executable = '"{0}"'.format(INTERPRETER_EXECUTABLE)
        mimodd_command = '{0} -m MiModD'.format(interpreter_executable)
        for wrapper in os.listdir(tool_wrapper_dir):
            with open(os.path.join(tool_wrapper_dir, wrapper),
                      'r', encoding='utf-8') as wrapper_fileobj:
                try:
                    wrapper_tree = ET.parse(wrapper_fileobj)
                except ET.ParseError:
                    galaxy_integration_warn(tool_wrapper_dir, wrapper)
                    continue
            wrapper_root = wrapper_tree.getroot()
            if not wrapper_root.tag == 'tool':
                galaxy_integration_warn(tool_wrapper_dir, wrapper)
                continue
            else:
                wrapper_version_element = wrapper_root.find('version_command')
                wrapper_version_element.text = \
                    wrapper_version_element.text.replace('mimodd',
                                                         mimodd_command)
                wrapper_command_element = wrapper_root.find('command')
                wrapper_command_element.text = \
                    wrapper_command_element.text.replace('mimodd',
                                                         mimodd_command)
                wrapper_tree.write(os.path.join(tool_wrapper_dir, wrapper),
                                   encoding='utf-8')

                
def galaxy_integration_warn(tool_wrapper_dir, wrapper):
    print()
    print('    Galaxy Integration Warning: File {0} in Galaxy tool wrapper directory {1} cannot be parsed as a wrapper xml.'
          .format(wrapper, tool_wrapper_dir))


DEFAULTCONFIG = """\
# USER-CONTROLLED SETTINGS
tmpfiles_path = r'/var/tmp'
multithreading_level = 4
max_memory = 2
snpeff_path = r''

# INSTALLATION SETTINGS
# DON'T CHANGE!

bin_path = r'../bin'
"""
