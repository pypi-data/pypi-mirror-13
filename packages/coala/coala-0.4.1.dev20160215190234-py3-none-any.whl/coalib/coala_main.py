from pyprint.ConsolePrinter import ConsolePrinter
import os

from coalib import coala_delete_orig
from coalib.output.printers.LogPrinter import LogPrinter
from coalib.processes.Processing import execute_section, simplify_section_result
from coalib.settings.ConfigurationGathering import gather_configuration
from coalib.misc.Exceptions import get_exitcode
from coalib.collecting.Collectors import collect_all_bears_from_sections
from coalib.output.Interactions import fail_acquire_settings
from coalib.output.Tagging import tag_results, delete_tagged_results


do_nothing = lambda *args: True


def run_coala(log_printer=None,
              print_results=do_nothing,
              acquire_settings=fail_acquire_settings,
              print_section_beginning=do_nothing,
              nothing_done=do_nothing,
              show_bears=do_nothing,
              autoapply=True):
    """
    This is a main method that should be usable for almost all purposes and
    reduces executing coala to one function call.

    :param log_printer:             A LogPrinter object to use for logging.
    :param print_results:           A callback that takes a LogPrinter, a
                                    section, a list of results to be printed,
                                    the file dict and the mutable file diff
                                    dict.
    :param acquire_settings:        The method to use for requesting settings.
                                    It will get a parameter which is a
                                    dictionary with the settings name as key
                                    and a list containing a description in [0]
                                    and the names of the bears who need this
                                    setting in all following indexes.
    :param print_section_beginning: A callback that will be called with a
                                    section name string whenever analysis of a
                                    new section is started.
    :param nothing_done:            A callback that will be called with only a
                                    log printer that shall indicate that
                                    nothing was done.
    :param show_bears:              A callback that will be called with first
                                    a list of local bears, second a list of
                                    global bears to output them. A third bool
                                    parameter may be used to indicate if a
                                    compressed output (True) or a normal output
                                    (False) is desired, the former being used
                                    for showing all available bears to the
                                    user.
    :param autoapply:               Set to False to autoapply nothing by
                                    default; this is overridable via any
                                    configuration file/CLI.
    :return:                        A dictionary containing a list of results
                                    for all analyzed sections as key.
    """
    log_printer = log_printer or LogPrinter(ConsolePrinter())

    exitcode = 0
    results = None
    try:
        yielded_results = yielded_unfixed_results = False
        did_nothing = True
        sections, local_bears, global_bears, targets = gather_configuration(
            acquire_settings,
            log_printer,
            autoapply=autoapply)

        tag = str(sections['default'].get('tag', None))
        dtag = str(sections['default'].get('dtag', None))
        config_file = os.path.abspath(str(sections["default"].get("config")))
        show_all_bears = bool(sections['default'].get('show_all_bears', False))
        show_bears_ = bool(sections["default"].get("show_bears", "False"))

        # Deleting all .orig files, so the latest files are up to date!
        coala_delete_orig.main(log_printer, sections["default"])

        delete_tagged_results(dtag, config_file, log_printer)

        if show_bears_ or show_all_bears:
            if show_all_bears:
                (local_bears,
                 global_bears) = collect_all_bears_from_sections(sections,
                                                                 log_printer)
            show_bears(local_bears, global_bears, show_all_bears)
            did_nothing = False
        else:
            results = {}
            for section_name, section in sections.items():
                if not section.is_enabled(targets):
                    continue

                print_section_beginning(section)
                section_result = execute_section(
                    section=section,
                    global_bear_list=global_bears[section_name],
                    local_bear_list=local_bears[section_name],
                    print_results=print_results,
                    log_printer=log_printer)
                yielded, yielded_unfixed, results[section_name] = (
                    simplify_section_result(section_result))

                yielded_results = yielded_results or yielded
                yielded_unfixed_results = (
                    yielded_unfixed_results or yielded_unfixed)
                did_nothing = False

            tag_results(tag, config_file, results, log_printer)

        if did_nothing:
            nothing_done(log_printer)
        elif yielded_unfixed_results:
            exitcode = 1
        elif yielded_results:
            exitcode = 5
    except BaseException as exception:  # pylint: disable=broad-except
        exitcode = exitcode or get_exitcode(exception, log_printer)

    return results, exitcode
