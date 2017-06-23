# Written by Eric Martel (emartel@gmail.com / www.ericmartel.com)

# Direct port of the Sublime Text 2 version also available on my github, see README.md for more info.

import sublime
import sublime_plugin

import os
import stat
import subprocess
import tempfile
import threading
import json
import sys
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x
# Plugin Settings are located in 'perforce.sublime-settings' make a copy in the User folder to keep changes

# global variable used when calling p4 - it stores the path of the file in the current view, used to determine with P4CONFIG to use
# whenever a view is selected, the variable gets updated
global_folder = ''

class PerforceP4CONFIGHandler(sublime_plugin.EventListener):
    def on_activated(self, view):
        if view.file_name():
            global global_folder
            global_folder, filename = os.path.split(view.file_name())

# Executed at startup to store the path of the plugin... necessary to open files relative to the plugin
perforceplugin_dir = os.getcwd()

class PerforceViewFileHistoryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileName = self.view.file_name()
        port = GetServerAddressFromClientspec()
        userName = GetUserFromClientspec()
        client = GetClientNameFromClientspec()

        import subprocess
        command = "p4v.exe -p {} -c {} -u {} -cmd \"history {}\"".format(port, client, userName, fileName)
        print(command)
        subprocess.call(command, shell=True)

class PerforceViewPropertiesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileName = self.view.file_name()
        port = GetServerAddressFromClientspec()
        userName = GetUserFromClientspec()
        client = GetClientNameFromClientspec()

        import subprocess
        command = "p4v.exe -p {} -c {} -u {} -cmd \"properties {}\"".format(port, client, userName, fileName)
        print(command)
        subprocess.call(command, shell=True)

class PerforceViewDiffDialogCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileName = self.view.file_name()
        port = GetServerAddressFromClientspec()
        userName = GetUserFromClientspec()
        client = GetClientNameFromClientspec()

        import subprocess
        command = "p4v.exe -p {} -c {} -u {} -cmd \"diffdialog {}\"".format(port, client, userName, fileName)
        print(command)
        subprocess.call(command, shell=True)

class PerforceViewPreviousDiffCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileName = self.view.file_name()
        port = GetServerAddressFromClientspec()
        userName = GetUserFromClientspec()
        client = GetClientNameFromClientspec()

        import subprocess
        command = "p4v.exe -p {} -c {} -u {} -cmd \"prevdiff {}\"".format(port, client, userName, fileName)
        print(command)
        subprocess.call(command, shell=True)

class PerforceViewTimeLapseViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileName = self.view.file_name()
        port = GetServerAddressFromClientspec()
        userName = GetUserFromClientspec()
        client = GetClientNameFromClientspec()

        import subprocess
        command = "p4v.exe -p {} -c {} -u {} -cmd \"annotate {}\"".format(port, client, userName, fileName)
        print(command)
        subprocess.call(command, shell=True)

class PerforceViewTreeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fileName = self.view.file_name()
        port = GetServerAddressFromClientspec()
        userName = GetUserFromClientspec()
        client = GetClientNameFromClientspec()

        import subprocess
        command = "p4v.exe -p {} -c {} -u {} -cmd \"tree {}\"".format(port, client, userName, fileName)
        print(command)
        subprocess.call(command, shell=True)



# Utility functions
def ConstructCommand(in_command):
    perforce_settings = sublime.load_settings('Perforce.sublime-settings')
    p4Env = perforce_settings.get('perforce_p4env')
    p4Path = perforce_settings.get('perforce_p4path')
    if ( p4Path == None or p4Path == '' ):
        p4Path = ''
    command = ''
    if(p4Env and p4Env != ''):
        command = '. {0} && {1}'.format(p4Env, p4Path)
    elif(sublime.platform() == "osx"):
        command = '. ~/.bash_profile && {0}'.format(p4Path)
    # Revert change until threading is fixed
    # command = getPerforceConfigFromPreferences(command)
    command += in_command
    return command

def getPerforceConfigFromPreferences(command):
    perforce_settings = sublime.load_settings('Perforce.sublime-settings')

    # check to see if the sublime preferences include the given p4 config
    # if it does, then add it to the command in the form "var=value command"
    # so that they get inserted into the environment the command runs in
    def addP4Var(command, var):
        p4var = perforce_settings.get(var)
        if p4var:
            if sublime.platform() == "windows":
                return command + "SET {0}={1} && ".format(var, p4var)
            return "{0}{1}={2} ".format(command, var, p4var)
        return command
    command = addP4Var(command, "P4PORT")
    command = addP4Var(command, "P4CLIENT")
    command = addP4Var(command, "P4USER")
    command = addP4Var(command, "P4PASSWD")
    return command

def GetUserFromClientspec():
    command = ConstructCommand('p4 info')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        WarnUser("usererr {0}".format(err.strip()))
        return -1

    # locate the line containing "User name: " and extract the following name
    startindex = result.find("User name: ")
    if(startindex == -1):
        WarnUser("Unexpected output from 'p4 info'.")
        return -1

    startindex += 11 # advance after 'User name: '

    endindex = result.find("\n", startindex)
    if(endindex == -1):
        WarnUser("Unexpected output from 'p4 info'.")
        return -1

    return result[startindex:endindex].strip();

def GetClientNameFromClientspec():
    command = ConstructCommand('p4 info')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        WarnUser("usererr {0}".format(err.strip()))
        return -1

    # locate the line containing "Client name: " and extract the following name
    startindex = result.find("Client name: ")
    if(startindex == -1):
        WarnUser("Unexpected output from 'p4 info'.")
        return -1

    startindex += 13 # advance after 'Client name: '

    endindex = result.find("\n", startindex)
    if(endindex == -1):
        WarnUser("Unexpected output from 'p4 info'.")
        return -1

    return result[startindex:endindex].strip();

def GetServerAddressFromClientspec():
    command = ConstructCommand('p4 info')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        WarnUser("usererr {0}".format(err.strip()))
        return -1

    # locate the line containing "Server address: " and extract the following name
    startindex = result.find("Server address: ")
    if(startindex == -1):
        WarnUser("Unexpected output from 'p4 info'.")
        return -1

    startindex += 16 # advance after 'Server address: '

    endindex = result.find("\n", startindex)
    if(endindex == -1):
        WarnUser("Unexpected output from 'p4 info'.")
        return -1

    return result[startindex:endindex].strip();

def GetClientRoot(in_dir):
    # check if the file is in the depot
    command = ConstructCommand('p4 info')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        WarnUser(err.strip())
        return -1

    # locate the line containing "Client root: " and extract the following path
    startindex = result.find("Client root: ")
    if(startindex == -1):
        # sometimes the clientspec is not displayed
        sublime.error_message("Perforce Plugin: p4 info didn't supply a valid clientspec, launching p4 client");
        command = ConstructCommand('p4 client')
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
        result, err = p.communicate()
        return -1

    startindex += 13 # advance after 'Client root: '

    endindex = result.find("\n", startindex)
    if(endindex == -1):
        WarnUser("Unexpected output from 'p4 info'.")
        return -1

    # convert all paths to "os.sep" slashes
    convertedclientroot = result[startindex:endindex].strip().replace('\\', os.sep).replace('/', os.sep)

    return convertedclientroot


def IsFolderUnderClientRoot(in_folder):
    # check if the file is in the depot
    clientroot = GetClientRoot(in_folder)
    if(clientroot == -1):
        return 0

    clientroot = clientroot.lower()
    if(clientroot == "null"):
        return 1;

    # convert all paths to "os.sep" slashes
    convertedfolder = in_folder.lower().replace('\\', os.sep).replace('/', os.sep);
    clientrootindex = convertedfolder.find(clientroot);

    if(clientrootindex == -1):
        return 0

    return 1

def IsFileInDepot(in_folder, in_filename):
    isUnderClientRoot = IsFolderUnderClientRoot(in_folder);
    if(os.path.isfile(os.path.join(in_folder, in_filename))): # file exists on disk, not being added
        if(isUnderClientRoot):
            return 1
        else:
            return 0
    else:
        if(isUnderClientRoot):
            return -1 # will be in the depot, it's being added
        else:
            return 0

def GetPendingChangelists():
    # Launch p4 changes to retrieve all the pending changelists
    currentuser = GetUserFromClientspec()
    if(currentuser == -1):
        return 0, "Unexpected output from 'p4 info'."

    command = ConstructCommand('p4 changes -s pending -u {0}'.format(currentuser))

    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")
    if(not err):
        return 1, result
    return 0, result

def AppendToChangelistDescription(changelist, input):
    # First, create an empty changelist, we will then get the cl number and set the description
    command = ConstructCommand('p4 change -o {0}'.format(changelist))
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        return 0, err

    # Find the description field and modify it
    lines = result.splitlines()

    descriptionindex = -1
    for index, line in enumerate(lines):
        if(line.strip() == "Description:"):
            descriptionindex = index
            break;

    filesindex = -1
    for index, line in enumerate(lines):
        if(line.strip() == "Files:"):
            filesindex = index
            break;

    if(filesindex == -1): # The changelist is empty
        endindex = index
    else:
        endindex = filesindex - 1

    perforce_settings = sublime.load_settings('Perforce.sublime-settings')
    lines.insert(endindex , "\t{0}".format(input))

    temp_changelist_description_file = open(os.path.join(tempfile.gettempdir(), "tempchangelist.txt"), 'w')

    try:
        temp_changelist_description_file.write(perforce_settings.get('perforce_end_line_separator').join(lines))
    finally:
        temp_changelist_description_file.close()

    command = ConstructCommand('p4 change -i < {0}'.format(temp_changelist_description_file.name))
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    # Clean up
    os.unlink(temp_changelist_description_file.name)

    if(err):
        return 0, err

    return 1, result

def PerforceCommandOnFile(in_command, in_folder, in_filename):
    command = ConstructCommand('p4 {0} "{1}"'.format(in_command, in_filename))
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(not err):
        return 1, result.strip()
    else:
        return 0, err.strip()

def WarnUser(message):
    perforce_settings = sublime.load_settings('Perforce.sublime-settings')
    if(perforce_settings.get('perforce_warnings_enabled')):
        if(perforce_settings.get('perforce_log_warnings_to_status')):
            sublime.status_message("Perforce [warning]: {0}".format(message))
        else:
            print("Perforce [warning]: {0}".format(message))

def LogResults(success, message):
    if(success >= 0):
        print("Perforce: {0}".format(message))
    else:
        WarnUser(message);

def IsFileWritable(in_filename):
    if(not in_filename):
        return 0

    # if it doesn't exist, it's "writable"
    if(not os.path.isfile(in_filename)):
        return 1

    filestats = os.stat(in_filename)[0];
    if(filestats & stat.S_IWRITE):
        return 1
    return 0

# Checkout section
def Checkout(in_filename):
    if(IsFileWritable(in_filename)):
        return -1, "File is already writable."

    folder_name, filename = os.path.split(in_filename)
    isInDepot = IsFileInDepot(folder_name, filename)

    if(isInDepot != 1):
        return -1, "File is not under the client root."

    # check out the file
    return PerforceCommandOnFile("edit", folder_name, in_filename);

class PerforceAutoCheckout(sublime_plugin.EventListener):
    def on_modified(self, view):
        if(not view.file_name()):
            return

        if(IsFileWritable(view.file_name())):
            return

        perforce_settings = sublime.load_settings('Perforce.sublime-settings')

        # check if this part of the plugin is enabled
        if(not perforce_settings.get('perforce_auto_checkout') or not perforce_settings.get('perforce_auto_checkout_on_modified')):
            return

        if(view.is_dirty()):
            success, message = Checkout(view.file_name())
            LogResults(success, message);

    def on_pre_save(self, view):
        perforce_settings = sublime.load_settings('Perforce.sublime-settings')

        # check if this part of the plugin is enabled
        if(not perforce_settings.get('perforce_auto_checkout') or not perforce_settings.get('perforce_auto_checkout_on_save')):
            return

        if(view.is_dirty()):
            success, message = Checkout(view.file_name())
            LogResults(success, message);

class PerforceCheckoutCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if(self.view.file_name()):
            success, message = Checkout(self.view.file_name())
            LogResults(success, message)
        else:
            WarnUser("View does not contain a file")

class PerforceCheckoutAllOpenFilesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for view in self.view.window().views():
            Checkout(view.file_name())

# Add section
def Add(in_folder, in_filename):
    # add the file
    return PerforceCommandOnFile("add", in_folder, in_filename);

class PerforceAutoAdd(sublime_plugin.EventListener):
    preSaveIsFileInDepot = 0
    def on_pre_save(self, view):
        # file already exists, no need to add
        if view.file_name() and os.path.isfile(view.file_name()):
            return

        global global_folder
        global_folder, filename = os.path.split(view.file_name())

        perforce_settings = sublime.load_settings('Perforce.sublime-settings')

        self.preSaveIsFileInDepot = 0

        # check if this part of the plugin is enabled
        if(not perforce_settings.get('perforce_auto_add')):
            WarnUser("Auto Add disabled")
            return

        folder_name, filename = os.path.split(view.file_name())

        if(not IsFolderUnderClientRoot(folder_name)):
            WarnUser("Adding file outside of clientspec, ignored for auto add")
            return

        self.preSaveIsFileInDepot = IsFileInDepot(folder_name, filename)

    def on_post_save(self, view):
        if(self.preSaveIsFileInDepot == -1):
            folder_name, filename = os.path.split(view.file_name())
            success, message = Add(folder_name, filename)
            LogResults(success, message)

class PerforceAddCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if(self.view.file_name()):
            folder_name, filename = os.path.split(self.view.file_name())

            if(IsFileInDepot(folder_name, filename)):
                success, message = Add(folder_name, filename)
            else:
                success = 0
                message = "File is not under the client root."

            LogResults(success, message)
        else:
            WarnUser("View does not contain a file")

# Rename section
def Rename(in_filename, in_newname):
    command = ConstructCommand('p4 integrate -d -t -Di -f "{0}" "{1}"'.format(in_filename, in_newname))
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        return 0, err.strip()

    command = ConstructCommand('p4 delete "{0}" "{1}"'.format(in_filename, in_newname))
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(not err):
        return 1, result.strip()
    else:
        return 0, err.strip()

class PerforceRenameCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Get the description
        self.window.show_input_panel('New File Name', self.window.active_view().file_name(),
            self.on_done, self.on_change, self.on_cancel)

    def on_done(self, input):
        success, message = Rename(self.window.active_view().file_name(), input)
        if(success):
            self.window.run_command('close')
            self.window.open_file(input)

        LogResults(success, message)

    def on_change(self, input):
        pass

    def on_cancel(self):
        pass

# Delete section
def Delete(in_folder, in_filename):
    success, message = PerforceCommandOnFile("delete", in_folder, in_filename)
    if(success):
        # test if the file is deleted
        if(os.path.isfile(os.path.join(in_folder, in_filename))):
            success = 0

    return success, message

class PerforceDeleteCommand(sublime_plugin.WindowCommand):
    def run(self):
        if(self.window.active_view().file_name()):
            folder_name, filename = os.path.split(self.window.active_view().file_name())

            if(IsFileInDepot(folder_name, filename)):
                success, message = Delete(folder_name, filename)
                if(success): # the file was properly deleted on perforce, ask Sublime Text to close the view
                    self.window.run_command('close');
            else:
                success = 0
                message = "File is not under the client root."

            LogResults(success, message)
        else:
            WarnUser("View does not contain a file")

# Revert section
def Revert(in_folder, in_filename):
    # revert the file
    return PerforceCommandOnFile("revert", in_folder, in_filename);

class PerforceRevertCommand(sublime_plugin.TextCommand):
    def run_(self, edit_token, args): # revert cannot be called when an Edit object exists, manually handle the run routine
        if(self.view.file_name()):
            folder_name, filename = os.path.split(self.view.file_name())

            if(IsFileInDepot(folder_name, filename)):
                success, message = Revert(folder_name, filename)
                if(success): # the file was properly reverted, ask Sublime Text to refresh the view
                    self.view.run_command('revert');
            else:
                success = 0
                message = "File is not under the client root."

            LogResults(success, message)
        else:
            WarnUser("View does not contain a file")

# Diff section
def Diff(in_folder, in_filename):
    # diff the file
    return PerforceCommandOnFile("diff", in_folder, in_filename);

class PerforceDiffCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if(self.view.file_name()):
            folder_name, filename = os.path.split(self.view.file_name())

            if(IsFileInDepot(folder_name, filename)):
                success, message = Diff(folder_name, filename)
            else:
                success = 0
                message = "File is not under the client root."

            LogResults(success, message)
        else:
            WarnUser("View does not contain a file")

# Graphical Diff With Depot section
class GraphicalDiffThread(threading.Thread):
    def __init__(self, in_folder, in_filename, in_endlineseparator, in_command):
        self.folder = in_folder
        self.filename = in_filename
        self.endlineseparator = in_endlineseparator
        self.command = in_command
        threading.Thread.__init__(self)

    def run(self):
        success, content = PerforceCommandOnFile("print", self.folder, self.filename)
        if(not success):
            return 0, content

        # Create a temporary file to hold the depot version
        depotFileName = "depot"+self.filename
        tmp_file = open(os.path.join(tempfile.gettempdir(), depotFileName), 'w')

        # Remove the first two lines of content
        linebyline = content.splitlines();
        content=self.endlineseparator.join(linebyline[1:]);

        try:
            tmp_file.write(content)
        finally:
            tmp_file.close()

        # Launch P4Diff with both files and the same arguments P4Win passes it
        diffCommand = self.command
        diffCommand = diffCommand.replace('%depotfile_path', tmp_file.name)
        diffCommand = diffCommand.replace('%depotfile_name', depotFileName)
        diffCommand = diffCommand.replace('%file_path', os.path.join(self.folder, self.filename))
        diffCommand = diffCommand.replace('%file_name', self.filename)

        command = ConstructCommand(diffCommand)

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
        result, err = p.communicate()
        result = result.decode("utf-8")
        err = err.decode("utf-8")

        # Clean up
        os.unlink(tmp_file.name);

def GraphicalDiffWithDepot(self, in_folder, in_filename):
    perforce_settings = sublime.load_settings('Perforce.sublime-settings')
    diffcommand = perforce_settings.get('perforce_selectedgraphicaldiffapp_command')
    if not diffcommand:
        diffcommand = perforce_settings.get('perforce_default_graphical_diff_command')
    GraphicalDiffThread(in_folder, in_filename, perforce_settings.get('perforce_end_line_separator'), diffcommand).start()

    return 1, "Launching thread for Graphical Diff"

class PerforceGraphicalDiffWithDepotCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if(self.view.file_name()):
            folder_name, filename = os.path.split(self.view.file_name())

            if(IsFileInDepot(folder_name, filename)):
                success, message = GraphicalDiffWithDepot(self, folder_name, filename)
            else:
                success = 0
                message = "File is not under the client root."

            LogResults(success, message)
        else:
            WarnUser("View does not contain a file")

class PerforceSelectGraphicalDiffApplicationCommand(sublime_plugin.WindowCommand):
    def run(self):
        diffapps = []
        if os.path.exists(perforceplugin_dir + os.sep + 'graphicaldiffapplications.json'):
            f = open(perforceplugin_dir + os.sep + 'graphicaldiffapplications.json')
            applications = json.load(f)
            f.close()

            for entry in applications.get('applications'):
                formattedentry = []
                formattedentry.append(entry.get('name'))
                formattedentry.append(entry.get('exename'))
                diffapps.append(formattedentry)

        self.window.show_quick_panel(diffapps, self.on_done)
    def on_done(self, picked):
        if picked == -1:
            return

        f = open(perforceplugin_dir + os.sep + 'graphicaldiffapplications.json')
        applications = json.load(f)
        entry = applications.get('applications')[picked]
        f.close()

        sublime.status_message(__name__ + ': Please make sure that {0} is reachable - you might need to restart Sublime Text 2.'.format(entry['exename']))

        settings = sublime.load_settings('Perforce.sublime-settings')
        settings.set('perforce_selectedgraphicaldiffapp', entry['name'])
        settings.set('perforce_selectedgraphicaldiffapp_command', entry['diffcommand'])
        sublime.save_settings('Perforce.sublime-settings')

# List Checked Out Files section
class ListCheckedOutFilesThread(threading.Thread):
    def __init__(self, window):
        self.window = window
        threading.Thread.__init__(self)

    def ConvertFileNameToFileOnDisk(self, in_filename):
        clientroot = GetClientRoot(os.path.dirname(in_filename))
        if(clientroot == -1):
            return 0

        if(clientroot == "null"):
            return in_filename;

        filename = clientroot + os.sep + in_filename.replace('\\', os.sep).replace('/', os.sep)

        return filename

    def MakeFileListFromChangelist(self, in_changelistline):
        files_list = []
        currentuser = GetUserFromClientspec()
        # Launch p4 opened to retrieve all files from changelist
        command = ConstructCommand('p4 opened -c {0} -u {1}'.format(in_changelistline[1], currentuser))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
        result, err = p.communicate()
        result = result.decode("utf-8")
        err = err.decode("utf-8")
        if(not err):
            lines = result.splitlines()
            for line in lines:
                # remove the change #
                poundindex = line.rfind('#')
                cleanedfile = line[0:poundindex]

                # just keep the filename
                cleanedfile = '/'.join(cleanedfile.split('/')[3:])

                file_entry = [cleanedfile[cleanedfile.rfind('/')+1:]]
                file_entry.append("Changelist: {0}".format(in_changelistline[1]))
                file_entry.append(' '.join(in_changelistline[7:]));
                localfile = self.ConvertFileNameToFileOnDisk(cleanedfile)
                if(localfile != 0):
                    file_entry.append(localfile)
                    files_list.append(file_entry)

        return files_list

    def MakeCheckedOutFileList(self):
        files_list = self.MakeFileListFromChangelist(['','default','','','','','','Default Changelist']);

        currentuser = GetUserFromClientspec()
        if(currentuser == -1):
            return files_list

        # Launch p4 changes to retrieve all the pending changelists
        command = ConstructCommand('p4 changes -s pending -u {0}'.format(currentuser));

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
        result, err = p.communicate()
        result = result.decode("utf-8")
        err = err.decode("utf-8")

        if(not err):
            changelists = result.splitlines()

            # for each line, extract the change, and run p4 opened on it to list all the files
            for changelistline in changelists:
                changelistlinesplit = changelistline.split(' ')
                files_list.extend(self.MakeFileListFromChangelist(changelistlinesplit))

        return files_list

    def run(self):
        self.files_list = self.MakeCheckedOutFileList()

        def show_quick_panel():
            if not self.files_list:
                sublime.error_message(__name__ + ': There are no checked out files to list.')
                return
            self.window.show_quick_panel(self.files_list, self.on_done)
        sublime.set_timeout(show_quick_panel, 10)

    def on_done(self, picked):
        if picked == -1:
            return
        file_name = self.files_list[picked][3]

        def open_file():
            self.window.open_file(file_name)
        sublime.set_timeout(open_file, 10)


class PerforceListCheckedOutFilesCommand(sublime_plugin.WindowCommand):
    def run(self):
        ListCheckedOutFilesThread(self.window).start()

# Create Changelist section
def CreateChangelist(description):
    # First, create an empty changelist, we will then get the cl number and set the description
    command = ConstructCommand('p4 change -o')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        return 0, err

    # Find the description field and modify it
    desclabel = 'Description:{0}'.format(os.linesep)
    descindex = result.find(desclabel) + len(desclabel)
    descend = result.find(os.linesep*2, descindex)
    result = '{0}\t{1}{2}'.format(result[0:descindex], description, result[descend:])

    # Remove all files from the query, we want them to stay in Default
    filesindex = result.rfind("Files:")
    # The Files: section we want to get rid of is only present if there's files in the default changelist
    if(filesindex > 640):
        result = result[0:filesindex];

    temp_changelist_description_file = open(os.path.join(tempfile.gettempdir(), "tempchangelist.txt"), 'w')

    try:
        temp_changelist_description_file.write(result)
    finally:
        temp_changelist_description_file.close()

    command = ConstructCommand('p4 change -i < {0}'.format(temp_changelist_description_file.name))
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    # Clean up
    os.unlink(temp_changelist_description_file.name)

    if(err):
        return 0, err

    return 1, result

class PerforceCreateChangelistCommand(sublime_plugin.WindowCommand):
    def run(self):
        # Get the description
        self.window.show_input_panel('Changelist Description', '',
            self.on_done, self.on_change, self.on_cancel)

    def on_done(self, input):
        success, message = CreateChangelist(input)
        LogResults(success, message)

    def on_change(self, input):
        pass

    def on_cancel(self):
        pass

# Move Current File to Changelist
def MoveFileToChangelist(in_filename, in_changelist):
    folder_name, filename = os.path.split(in_filename)

    command = ConstructCommand('p4 reopen -c {0} "{1}"'.format(in_changelist, filename))
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
    result, err = p.communicate()
    result = result.decode("utf-8")
    err = err.decode("utf-8")

    if(err):
        return 0, err

    return 1, result

class ListChangelistsAndMoveFileThread(threading.Thread):
    def __init__(self, window):
        self.window = window
        self.view = window.active_view()
        threading.Thread.__init__(self)

    def MakeChangelistsList(self):
        success, rawchangelists = GetPendingChangelists();

        resultchangelists = ['New', 'Default'];

        if(success):
            changelists = rawchangelists.splitlines()

            # for each line, extract the change
            for changelistline in changelists:
                changelistlinesplit = changelistline.split(' ')

                # Insert at two because we receive the changelist in the opposite order and want to keep new and default on top
                resultchangelists.insert(2, "Changelist {0} - {1}".format(changelistlinesplit[1], ' '.join(changelistlinesplit[7:])))

        return resultchangelists

    def run(self):
        self.changelists_list = self.MakeChangelistsList()

        def show_quick_panel():
            if not self.changelists_list:
                sublime.error_message(__name__ + ': There are no changelists to list.')
                return
            self.window.show_quick_panel(self.changelists_list, self.on_done)

        sublime.set_timeout(show_quick_panel, 10)

    def on_done(self, picked):
        if picked == -1:
            return
        changelistlist = self.changelists_list[picked].split(' ')

        def move_file():
            changelist = 'Default'
            if(len(changelistlist) > 1): # Numbered changelist
                changelist = changelistlist[1]
            else:
                changelist = changelistlist[0]

            if(changelist == 'New'): # Special Case
                self.window.show_input_panel('Changelist Description', '', self.on_description_done, self.on_description_change, self.on_description_cancel)
            else:
                success, message = MoveFileToChangelist(self.view.file_name(), changelist.lower())
                LogResults(success, message);

        sublime.set_timeout(move_file, 10)

    def on_description_done(self, input):
        success, message = CreateChangelist(input)
        if(success == 1):
            # Extract the changelist name from the message
            changelist = message.split(' ')[1]
            # Move the file
            success, message = MoveFileToChangelist(self.view.file_name(), changelist)

        LogResults(success, message)

    def on_description_change(self, input):
        pass

    def on_description_cancel(self):
        pass

class PerforceMoveCurrentFileToChangelistCommand(sublime_plugin.WindowCommand):
    def run(self):
        # first, test if the file is under the client root
        folder_name, filename = os.path.split(self.window.active_view().file_name())
        isInDepot = IsFileInDepot(folder_name, filename)

        if(isInDepot != 1):
            WarnUser("File is not under the client root.")
            return 0

        ListChangelistsAndMoveFileThread(self.window).start()

# Add Line to Changelist Description
class AddLineToChangelistDescriptionThread(threading.Thread):
    def __init__(self, window):
        self.window = window
        self.view = window.active_view()
        threading.Thread.__init__(self)

    def MakeChangelistsList(self):
        success, rawchangelists = GetPendingChangelists();

        resultchangelists = [];

        if(success):
            changelists = rawchangelists.splitlines()

            # for each line, extract the change, and run p4 opened on it to list all the files
            for changelistline in changelists:
                changelistlinesplit = changelistline.split(' ')

                # Insert at zero because we receive the changelist in the opposite order
                # Might be more efficient to sort...
                changelist_entry = ["Changelist {0}".format(changelistlinesplit[1])]
                changelist_entry.append(' '.join(changelistlinesplit[7:]));

                resultchangelists.insert(0, changelist_entry)

        return resultchangelists

    def run(self):
        self.changelists_list = self.MakeChangelistsList()

        def show_quick_panel():
            if not self.changelists_list:
                sublime.error_message(__name__ + ': There are no changelists to list.')
                return
            self.window.show_quick_panel(self.changelists_list, self.on_done)

        sublime.set_timeout(show_quick_panel, 10)

    def on_done(self, picked):
        if picked == -1:
            return
        changelistlist = self.changelists_list[picked][0].split(' ')

        def get_description_line():
            self.changelist = changelistlist[1]
            self.window.show_input_panel('Changelist Description', '', self.on_description_done, self.on_description_change, self.on_description_cancel)

        sublime.set_timeout(get_description_line, 10)

    def on_description_done(self, input):
        success, message = AppendToChangelistDescription(self.changelist, input)

        LogResults(success, message)

    def on_description_change(self, input):
        pass

    def on_description_cancel(self):
        pass

class PerforceAddLineToChangelistDescriptionCommand(sublime_plugin.WindowCommand):
    def run(self):
        AddLineToChangelistDescriptionThread(self.window).start()

# Submit section
class SubmitThread(threading.Thread):
    def __init__(self, window):
        self.window = window
        self.view = window.active_view()
        threading.Thread.__init__(self)

    def MakeChangelistsList(self):
        success, rawchangelists = GetPendingChangelists();

        resultchangelists = ['Default'];

        currentuser = GetUserFromClientspec();
        command = ConstructCommand('p4 opened -c default -u {0}'.format(currentuser))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
        result, err = p.communicate()
        result = result.decode("utf-8")
        err = err.decode("utf-8")

        if err:
            resultchangelists.pop()

        if success:
            changelists = rawchangelists.splitlines()

            # for each line, extract the change
            for changelistline in changelists:
                changelistlinesplit = changelistline.split(' ')

                # Insert at two because we receive the changelist in the opposite order and want to keep default on top
                resultchangelists.insert(1, "Changelist {0} - {1}".format(changelistlinesplit[1], ' '.join(changelistlinesplit[7:])))

        return resultchangelists

    def run(self):
        self.changelists_list = self.MakeChangelistsList()

        def show_quick_panel():
            if not self.changelists_list:
                sublime.error_message(__name__ + ': There are no changelists to list.')
                return
            self.window.show_quick_panel(self.changelists_list, self.on_done)

        sublime.set_timeout(show_quick_panel, 10)

    def on_done(self, picked):
        if picked == -1:
            return
        changelist = self.changelists_list[picked]
        changelistsections = changelist.split(' ')

        command = ''
        # Check in the selected changelist
        if changelistsections[0] != 'Default':
            command = ConstructCommand('p4 submit -c {0}'.format(changelistsections[1]))
        else:
            command = ConstructCommand('p4 submit')
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
        result, err = p.communicate()
        result = result.decode("utf-8")
        err = err.decode("utf-8")

    def on_description_change(self, input):
        pass

    def on_description_cancel(self):
        pass

class PerforceSubmitCommand(sublime_plugin.WindowCommand):
    def run(self):
        SubmitThread(self.window).start()


class PerforceLogoutCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            command = ConstructCommand("p4 set P4PASSWD=")
            p = subprocess.Popen(command, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
            p.communicate()
        except ValueError:
            pass

class PerforceLoginCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Enter Perforce Password", "", self.on_done, None, None)

    def on_done(self, password):
        try:
            command = ConstructCommand("p4 logout")
            p = subprocess.Popen(command, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
            p.communicate()
            #unset var
            command = ConstructCommand("p4 set P4PASSWD={0}".format(password))
            p = subprocess.Popen(command, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
            p.communicate()
        except ValueError:
            pass

class PerforceUnshelveClCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            ShelveClCommand(self.window, False).start()
        except:
            WarnUser("Unknown Error, does the included P4 Version support Shelve?")
            return -1
class PerforceShelveClCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            ShelveClCommand(self.window, True).start()
        except:
            WarnUser("Unknown Error, does the included P4 Version support Shelve?")
            return -1

class ShelveClCommand(threading.Thread):
    def __init__(self, window, shelve=True):
        self.shelve = shelve
        self.window = window
        threading.Thread.__init__(self)

    def run(self):
        self.changelists_list = self.MakeChangelistsList()
        def show_quick_panel():
            if not self.changelists_list:
                sublime.error_message(__name__ + ': There are no changelists to list.')
                return
            self.window.show_quick_panel(self.changelists_list, self.on_done)

        sublime.set_timeout(show_quick_panel, 10)

    def on_done(self, picked):
        if picked == -1:
            return
        changelistlist = self.changelists_list[picked].split(' ')


        changelist = 'Default'
        if(len(changelistlist) > 1): # Numbered changelist
            changelist = changelistlist[1]
        else:
            changelist = changelistlist[0]

        if self.shelve:
            cmdString = "shelve -c{0}".format(changelist)
        else:
            cmdString = "unshelve -s{0} -f".format(changelist)
        command = ConstructCommand("p4 {0}".format(cmdString))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=global_folder, shell=True)
        result, err = p.communicate()
        result = result.decode("utf-8")
        err = err.decode("utf-8")

        if(err):
            WarnUser("usererr {0}".format(err.strip()))
            return -1

    def MakeChangelistsList(self):
        success, rawchangelists = GetPendingChangelists();

        resultchangelists = []

        if(success):
            changelists = rawchangelists.splitlines()

            # for each line, extract the change
            for changelistline in changelists:
                changelistlinesplit = changelistline.split(' ')

                resultchangelists.insert(0, "Changelist {0} - {1}".format(changelistlinesplit[1], ' '.join(changelistlinesplit[7:])))

        return resultchangelists
