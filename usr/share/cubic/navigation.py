#!/usr/bin/python3

########################################################################
#                                                                      #
# navigation.py                                                        #
#                                                                      #
# Copyright (C) 2020 PJ Singh <psingh.cubic@gmail.com>                 #
#                                                                      #
########################################################################

########################################################################
#                                                                      #
# This file is part of Cubic - Custom Ubuntu ISO Creator.              #
#                                                                      #
# Cubic is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# Cubic is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with Cubic. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                      #
########################################################################
"""
Controls transitions between pages based on automatic or user initiated
actions.

Valid actions for each page must be configured in the get_new_page()
function of this module.

Pages
-----

All pages that work with the navigation module must have the following
parameter and three functions:

name
- The page name as a string.
- Must match the module name.
- Valid page names must be suffixed with '_page' and contain lower case
  alpha characters, numbers, or underscore characters ('_').
- Examples: 'start_page', 'project_page'

setup(action, old_page=None)
- Prepare the current page before displaying it.
- Setup navigation buttons' style, visibility, sensitivity, and actions.
- Activate navigation buttons, and show other buttons as necessary.
- Executed prior to the enter() function.
- Process the action from the prior page (such as 'back' or 'next').
- Return 'error' to automatically transfer to an error page (as
  specified in the navigation module's get_new_page() function).
- Return None to display the current page and execute the the enter()
  function.

enter(action, old_page=None)
- Process the current page after displaying it.
- Only change buttons during validation.
- Executed after the setup() function.
- Process the action from the prior page (such as 'back' or 'next').
- Return 'error' to automatically transfer to an error page (as
  specified in the navigation module's get_new_page() function).
- Return None to stay on the current page.
- Return an action (such as 'next') to automatically transfer to a page
  corresponding to the action (as specified in the navigation module's
  get_new_page() function).

leave(action, new_page=None)
- Process the current page after a user action (such as clicking the
  Back, Next, Copy, Delete, or Quit buttons).
- Deactivate navigation buttons, and hide other buttons as necessary.
- Process the action from the current page (such as 'back', 'next',
  'copy', 'delete', or 'quit').
- Return 'error' to automatically transfer to an error page (as
  specified in the navigation module's get_new_page() function); in most
  cases, the current page should be the 'error' page, since error
  messages will be displayed directly on the current page.
- Return None to automatically transfer to a page corresponding to the
  action from the current page (as specified in the navigation module's
  get_new_page() function).

Handling Errors During Automatic Transitions
--------------------------------------------

There are two options to handle errors on a page during automatic
transitions.

1. The page can return 'error' from the enter() function. This is the
   preferred option for automatic transitions because error pages can be
   explicitly configured in the get_new_page() function.
   a. The new page for action 'error' can be the current page. This is
      the preferred approach when the current page is able to display
      the appropriate error information. The Next button must be
      disabled, and the error must be displayed on the current page.
   b. The new page for action 'error' can be a different page.  Use this
      approach when the current page is not able to display the full
      error information.
2. The page can return None from the enter() function. This is not the
   preferred option for automatic transitions because the enter()
   function inconsistently returns None actions (for error situations)
   and non-None actions (for non-error) situations, and because the
   error pages are not explicitly configured in the get_new_page()
   function. In this case, the application will not automatically
   navigate to a new page. The error must be displayed on the current
   page, and the Next button must be disabled.

Summary
-------

1. Configure all actions and error pages in the get_new_page() function.
2. From a page's setup() function, always return an 'error' action if an
   error occurs, otherwise return None.
3. From a page's leave() function, always return an 'error' action if an
   error occurs, otherwise return None.
4. From a page's enter() function:
   a. Always return None to stay on the current page.
   b. Always return a non-None action, such as 'next', to automatically
      transition to a new page.
   c. Always return an 'error' action if an error occurs prior to an
      automatic transition. Optionally:
      - Configure the current page as the error page. Ensure the error
        is displayed on the current page.
      - Configure a different page as the error page.
   d. If an error occurs when an automatic transition is not required,
      optionally:
      - Disable the Next button, display the error, and return a None
        action to stay on the current page. This is the preferred
        approach.
      - Return an 'error' action to automatically transition to a
        configured error page.
5. To handle multiple errors on a page (from the setup(), enter(), or
   leave() functions) configure unique error actions (such as 'error_1',
   'error_2', or 'error_3') with corresponding error pages.
"""

from constants import BOLD_RED, BOLD_GREEN, BOLD_BLUE, BOLD_YELLOW, BOLD_MAGENTA, BOLD_CYAN, NORMAL, NEW_LINE
from utilities import display
from utilities import logger
from utilities import model
from utilities.process_utilities import terminate_process

import ctypes
import importlib
import os
from re import sub
from sys import stdout
from threading import Thread, current_thread
from time import sleep

########################################################################
# Constants
########################################################################

navigation_thread = None

########################################################################
# Exception Classes
########################################################################


class ModuleNotFoundError(Exception):
    """
    Exception raised by the get_page() function when page module does
    not exist.
    """

    pass


class InterruptException(Exception):
    """
    Exception used by the interrupt_navigation_thread() function to
    interrupt a running navigation thread.
    """

    def __str__(self):
        """
        The string representation of this exception used for display
        purposes.
        
        Returns:
            (str): 'Interrupt Exception'
        """

        return 'Interrupt Exception'


class InvalidActionException(Exception):
    """
    Exception raised by the get_new_page() function when an action has
    not been configured for the current page.
    """

    pass


########################################################################
# Handlers
########################################################################


def on_window_destroy(*args):

    logger.log_value('Clicked', 'Exit')
    # action = button.action
    action = 'quit'
    handle_navigation(action)
    # display.main_quit()


def on_clicked__navigation_button(button):

    display_label = sub('❬|❭', '', button.get_label())
    logger.log_value('Clicked', display_label)

    handle_navigation(button.action)


def on_clicked_website_menu_button(button):

    logger.log_title('Clicked website_menu_button')

    url = 'https://launchpad.net/cubic'
    command = 'xdg-open "%s" &' % url
    os.system(command)


def on_clicked_help_menu_button(button):

    logger.log_title('Cclicked help menu button')

    url = 'https://answers.launchpad.net/cubic'
    command = 'xdg-open "%s" &' % url
    os.system(command)


def on_clicked_page_help_menu_button(button):

    logger.log_title('Cclicked help menu button')

    url = model.help_urls[model.page.name]
    command = 'xdg-open "%s" &' % url
    os.system(command)


def on_clicked_donate_menu_button(button):

    logger.log_title('Clicked donate menu button')

    url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5WJL2ZE3AWGQQ&currency_code=USD&source=url'
    command = 'xdg-open "%s" &' % url
    os.system(command)


def on_clicked_about_menu_button(button):

    logger.log_title('Clicked about menu button')

    display.set_sensitive('window', False)
    display.show('about_dialog')

    # return True


def on_close_about_dialog(widget, event):

    logger.log_title('Clicked close about dialog')

    display.hide('about_dialog')
    display.set_sensitive('window', True)

    return True


########################################################################
# Navigation Functions
########################################################################


def handle_navigation(action):
    """
    Process a user initiated action (such as clicking Back, Next, Copy,
    Delete, or Quit buttons). This function must only be invoked by user
    interface handler functions, except when launching the application
    for the first time (with an 'open' action).
    
    This function will interrupt the previous navigation thread,
    determine the new page based on the user initiated action, and
    create and start a new navigation thread.

    Args:
        action (str): The user action (such as 'back', 'next', 'copy',
            'delete', 'quit', etc.). Valid actions for each page must be
            configured in the get_new_page() function.

    Returns:
        None
    """

    page_display_name = get_page_display_name(model.page)
    logger.log_title('Handle navigation from %s on %s action' % (page_display_name, action))

    # Interrupt the previous navigation thread.
    interrupt_navigation_thread()

    # Determine the new page based on the user initiated action.
    page = model.page
    new_page = get_new_page(action, page)

    # Create and start a new navigation thread.
    global navigation_thread
    navigation_thread = Thread(target=navigate, args=(action, page, new_page))
    navigation_thread.start()


def interrupt_navigation_thread():
    """
    Interrupts the current thread; this function is automatically
    invoked by the handle_navigation() function prior to navigating to a
    new page.
    
    This function will terminate the current process before terminating
    the navigation thread. In some cases, if there is no additional work
    for the thread to do after the process stops, the navigation thread
    may automatically end immediately after the process stops.
    """

    stdout.flush()

    # Terminate the process before terminating the navigation thread. In
    # some cases, if there is no additional work for the thread to do
    # after the process stops, the navigation thread may automatically
    # end immediately after the process stops.

    terminate_process()

    global navigation_thread
    if navigation_thread and navigation_thread.is_alive():

        navigation_thread_id = navigation_thread.ident
        logger.log_value('Interrupt previous thread with id', navigation_thread_id)

        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(navigation_thread_id), ctypes.py_object(InterruptException))
        navigation_thread.join()
        sleep(0.50)

        logger.log_value('Interrupted previous thread with id', navigation_thread_id)

    else:

        logger.log_value('Interrupt previous thread', 'No thread')


def navigate(action, page, new_page):
    """
    Process an automatic action (such as 'next' or 'error') by
    performing the following sequence of steps:

        1. Quit the application (on 'quit', 'exit', or 'close' actions)
        2. Leave the current page
        3. Setup the new page
        4. Show the new page
        5. Enter the new page

    This function is used as a thread by the by the handle_navigation()
    function and may call itself recursively. All invocations will run
    in the current navigation thread. The navigation thread ends when
    this function exists on a return statement, or when the thread is
    terminated using the interrupt_navigation_thread() function.
    Whenever the current navigation thread is terminated, the running
    process will be terminated first.

    Args:
        action (str): The automatic action to process.
        page (str): The current page that the action occurred on.
        new_page (str): The new page that should be displayed, as
             configured in the get_new_page() function.

    Returns:
        None
    """

    page_display_name = get_page_display_name(page)
    new_page_display_name = get_page_display_name(new_page)

    logger.log_title('Navigate from %s to %s on %s action' % (page_display_name, new_page_display_name, action))

    # Quit the application.

    if action in ('quit', 'exit', 'close'):
        page.leave(action, new_page)
        display.main_quit()
        return

    # Leave the current page.

    try:
        result = page.leave(action, new_page) if page else None
    except InterruptException as exception:
        logger.log_value('Error', exception)
        # logger.log_value('The tracekback is', traceback.format_exc())
        return
    if result:
        # Navigate to an error page.
        new_page = get_new_page(result, page)
        navigate(result, page, new_page)
        return

    # Setup the new page.

    try:
        result = new_page.setup(action, page) if new_page else None
    except InterruptException as exception:
        logger.log_value('Error', exception)
        # logger.log_value('The tracekback is', traceback.format_exc())
        return
    if result:
        # Navigate to an error page.
        new_page = get_new_page(result, page)
        navigate(result, page, new_page)
        return

    # Show the new page.

    display.transition(page, new_page)
    model.page = new_page

    # Enter the new page.

    try:
        result = new_page.enter(action, page) if new_page else None
    except InterruptException as exception:
        logger.log_value('Error', exception)
        # logger.log_value('The tracekback is', traceback.format_exc())
        return

    page = new_page
    new_page = None

    if result:
        # Automatically navigate to another page, based on result.
        # If result is 'error', automatically navigate to an error page.
        new_page = get_new_page(result, page)
        navigate(result, page, new_page)
        return
    else:
        # Stay on the new page if result is None (i.e., there is no
        # automatic transition).
        return


def get_page(page_name):
    """
    Get the page corresponding to the page name.
    
    Args:
        page_name (str): The name of the page.

    Returns:
        (module): The page corresponding to the page name or None,
            if a module matching page name is not found.
    """

    page = None

    if page_name:
        try:
            page = importlib.import_module('pages.%s' % page_name)
        except ModuleNotFoundError as exception:
            logger.log_value('Error', exception)

    return page


def get_page_name(page):
    """
    Get the page name from the page.
    
    Args:
        page (module): The page.

    Returns:
        (str): The name from the page (i.e., page.name), or None if page
            is None.
    """

    return page.name if page else None


def get_page_display_name(page):
    """
    Get the displayable page name for the page.
    
    Args:
        page (module): The page.

    Returns:
        (str): The name from the page with underscore ('_') characters
            replaced with space (' ') characters. If page is None,
            'no page' is returned.
    """

    return page.name.replace('_', ' ') if page else 'no page'


def get_new_page(action, page):
    """
    Gets the new page for the specified action on the current page. All
    valid actions for each page must be configured in this function. If
    an action has not been configured, then an InvalidActionException
    will be raised.

    Args:
        page (module): The current page.
        action (str): The action.

    Returns:
        (module): The new page.

    Raises:
        InvalidActionException: If the specified action has not been
        configured for the specified page.
    """

    # There are two ways to handle errors on a page.
    #
    # 1) The page can return 'error' from the enter function.
    #
    #    In this case, there must be an action specified below.
    #    a) The next page for action 'error' can be the current page.
    #    b) The next page for action 'error' can be a new page.
    #       This is the preferred approach when the current page is able
    #       to display the appropriate error information.
    #
    # 2) The page can return None.
    #    In this case, the page will not automatically navigate to a
    #    new page. The error must be displayed on the current page.
    #    This is the preferred approach when the current page is able to
    #    display the appropriate error information.

    page_name = get_page_name(page)

    page_display_name = get_page_display_name(page)
    logger.log_value('Current page', page_display_name)
    logger.log_value('Action', action)

    if page_name == None:
        if action == 'open':
            new_page_name = 'start_page'
        else:
            invalid_action(action, page)

    elif page_name == 'start_page':
        if action == 'next':
            new_page_name = 'project_page'
        elif action == 'migrate':
            new_page_name = 'migrate_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'migrate_page':
        if action == 'back':
            new_page_name = 'start_page'
        elif action == 'error':
            new_page_name = 'migrate_page'
        elif action == 'next':
            new_page_name = 'project_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'project_page':
        if action == 'back':
            new_page_name = 'start_page'
        elif action == 'delete':
            new_page_name = 'delete_page'
        elif action == 'next':
            new_page_name = 'extract_page'
        elif action == 'next_terminal_page':
            new_page_name = 'terminal_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'delete_page':
        if action == 'cancel':
            new_page_name = 'project_page'
        elif action == 'delete':
            new_page_name = 'project_page'
        elif action == 'error':
            new_page_name = 'delete_page'
        elif action == 'next':
            new_page_name = 'project_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'extract_page':
        if action == 'back':
            new_page_name = 'project_page'
        elif action == 'error':
            new_page_name = 'extract_page'
        elif action == 'next':
            new_page_name = 'terminal_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'terminal_page':
        if action == 'back':
            new_page_name = 'project_page'
        elif action == 'copy':
            new_page_name = 'copy_page'
        elif action == 'next':
            new_page_name = 'prepare_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'copy_page':
        if action == 'cancel':
            new_page_name = 'terminal_page'
        elif action == 'copy':
            new_page_name = 'terminal_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'prepare_page':
        if action == 'back':
            new_page_name = 'terminal_page'
        elif action == 'error':
            new_page_name = 'prepare_page'
        elif action == 'next':
            new_page_name = 'packages_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'packages_page':
        if action == 'back':
            new_page_name = 'terminal_page'
        elif action == 'next':
            new_page_name = 'options_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'options_page':
        if action == 'back':
            new_page_name = 'packages_page'
        elif action == 'generate':
            new_page_name = 'generate_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'generate_page':
        if action == 'back':
            new_page_name = 'options_page'
        elif action == 'finish':
            new_page_name = 'finish_page'
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    elif page_name == 'finish_page':
        if action == 'close':
            new_page_name = None
        elif action == 'quit':
            new_page_name = None
        else:
            invalid_action(action, page)

    new_page = get_page(new_page_name)
    page_display_name = get_page_display_name(new_page)
    logger.log_value('New page', page_display_name)

    return new_page


def invalid_action(action, page):
    """
    Raise an InvalidActionException to indicate that the specified
    action has not been configured for the specified page. This function
    is used by the get_new_page() function.

    Args:
        action (str): The action.
        page (module): The page module.

    Returns:
        This function always raises an exception.

    Raises:
        InvalidActionException: When this function is invoked.

    """

    page_display_name = get_page_display_name(page)
    raise InvalidActionException('Action "%s" is invalid for %s.' % (action, page_display_name))
