import os
import re
import json
from pprint import pprint
from subprocess import call
import sublime
import sublime_plugin
from shutil import copy2

try:
    from edit_buffer import *
    from statusprocess import *
    from asyncprocess import *
except ImportError:
    from .edit_buffer import *
    from .statusprocess import *
    from .asyncprocess import *

FOLDER = os.path.dirname(os.path.realpath(__file__))


def getDefaultConf():
    file_path = os.path.join(FOLDER, "global.json")
    return "\"" + file_path + "\""


def getTempConf():
    file_path = os.path.join(FOLDER, "config_file.txt")
    file = open(file_path, "r")
    file_path = file.read()
    if not file_path:
        return file_path
    else:
        return "\"" + file_path + "\""


def getCurrentTestRule():
    file_path = os.path.join(FOLDER, "current_test_rule.txt")
    file = open(file_path, "r")
    file_path = file.read()
    return file_path


RESULT_VIEW_NAME = 'eslint_result_view'
SETTINGS_FILE = "sublime-eslint.sublime-settings"
GLOBAL_CONFIG_FILE = getDefaultConf()
TEMP_CONFIG_FILE = getTempConf()


class EslintCommand(sublime_plugin.WindowCommand):
    def init(self):
        self.s = sublime.load_settings(SETTINGS_FILE)

        self.file_path = self.window.active_view().file_name()
        self.file_name = os.path.basename(self.file_path)
        self.debug = self.s.get('debug', False)
        self.buffered_data = ''
        self.is_running = True
        self.tests_panel_showed = False
        self.init_tests_panel()

    def run(self):
        self.init()

        GLOBAL_CONFIG_FILE = getDefaultConf()
        TEMP_CONFIG_FILE = getTempConf()

        rule_dir = os.path.join(FOLDER, "custom_rules")

        cmd = 'eslint ' + self.s.get('node_eslint_options',
                                     '') + ' "' + self.file_path + '"' + " --rulesdir " + '"' + rule_dir + '"' + " -c "
        if TEMP_CONFIG_FILE:
            cmd += TEMP_CONFIG_FILE
        else:
            cmd += GLOBAL_CONFIG_FILE

        print(cmd)
        AsyncProcess(cmd, self)
        StatusProcess('Starting ESLint for file ' + self.file_name, self)
        EsLintEventListener.disabled = True

    def init_tests_panel(self):
        if not hasattr(self, 'output_view'):
            self.output_view = self.window.get_output_panel(RESULT_VIEW_NAME)
            self.output_view.set_name(RESULT_VIEW_NAME)
        self.clear_test_view()
        self.output_view.settings().set("file_path", self.file_path)

    def show_tests_panel(self):
        if self.tests_panel_showed:
            return
        self.window.run_command("show_panel", {"panel": "output." + RESULT_VIEW_NAME})

        self.tests_panel_showed = True

    def clear_test_view(self):
        with Edit(self.output_view, True) as edit:
            edit.erase(sublime.Region(0, self.output_view.size()))

    # appending data to the result
    def append_data(self, proc, bData, end=False):
        if self.debug:
            print("DEBUG: append_data start")

        data = re.split(r'\s{2,}', bData.decode('utf-8'))
        count = 0
        data[count] += "\n"
        while count < len(data) - 2:

            if count % 4 == 0:
                data[count] += "\n"

            if (count + 1) % 4 == 0:
                data[count] += "\t"

            if (count + 2) % 4 == 0:
                data[count] += "\t"

            if (count + 3) % 4 == 0:
                temp = data[count].split(":")
                temp[0] = " Line No=> " + temp[0] + " "
                temp[1] = " Position=> " + temp[1] + " "
                data[count] = "".join(temp)

            count += 1

        data = " ".join(data)

        self.show_tests_panel()
        with Edit(self.output_view, True) as edit:
            try:
                edit.insert(self.output_view.size(), str(data))
            except UnicodeEncodeError:
                edit.insert(self.output_view.size(), unicode(data))


    def update_status(self, msg, progress):
        sublime.status_message(msg + " " + progress)

    def proc_terminated(self, proc):
        if proc.returncode == 0:
            msg = self.file_name + ' lint free!'
        else:
            msg = ''
        self.append_data(proc, msg.encode('utf-8'), True)

        EsLintEventListener.disabled = False


class EsLintEventListener(sublime_plugin.EventListener):
    # Eslint event
    disabled = False

    def __init__(self):
        self.previous_resion = None
        self.file_view = None

    def on_post_save(self, view):
        s = sublime.load_settings(SETTINGS_FILE)
        if s.get('run_on_save', False) is False:
            return

        if view.file_name().endswith('.js') is False:
            return

        # run eslint
        sublime.active_window().run_command("eslint")

    def on_deactivated(self, view):
        if view.name() != RESULT_VIEW_NAME:
            return
        self.previous_resion = None

        if self.file_view:
            self.file_view.erase_regions(RESULT_VIEW_NAME)

    def on_selection_modified(self, view):
        if EsLintEventListener.disabled:
            return
        if view.name() != RESULT_VIEW_NAME:
            return

        # RESULT_VIEW_NAME is a panel
        region = view.line(view.sel()[0])

        s = sublime.load_settings(SETTINGS_FILE)

        # make sure call once.
        if self.previous_resion == region:
            return
        self.previous_resion = region

        totalstring = view.substr(region)
        # extract line from eslint result.
        text = totalstring.split(' ')

        # validation for result region selection
        if 'Line' not in totalstring:
            return

        line = text[4]

        # hightlight view line.
        view.add_regions(RESULT_VIEW_NAME, [region], "comment")

        # find the file view.
        file_path = view.settings().get('file_path')
        window = sublime.active_window()
        file_view = None
        for v in window.views():
            if v.file_name() == file_path:
                file_view = v
                break
        if file_view is None:
            return

        self.file_view = file_view
        window.focus_view(file_view)
        file_view.run_command("goto_line", {"line": line})
        file_region = file_view.line(file_view.sel()[0])

        # # highlight file_view line

        if 'error' in totalstring:
            file_view.add_regions(RESULT_VIEW_NAME, [file_region], "invalid", "dot")
        else:
            file_view.add_regions(RESULT_VIEW_NAME, [file_region], "comment")


class ShowEslintResultCommand(sublime_plugin.WindowCommand):
    # show Eslint result

    def run(self):
        self.window.run_command("show_panel", {"panel": "output." + RESULT_VIEW_NAME})


class ConfigCommand(sublime_plugin.WindowCommand):
    def run(self):
        GLOBAL_CONFIG_FILE = getDefaultConf()
        TEMP_CONFIG_FILE = getTempConf()

        print(TEMP_CONFIG_FILE)
        print(GLOBAL_CONFIG_FILE)
        if TEMP_CONFIG_FILE:
            file = TEMP_CONFIG_FILE
        else:
            file = GLOBAL_CONFIG_FILE

        cmd1 = "cd " + FOLDER
        cmd = cmd1 + " && " + "java -jar " + "EslintEditor.jar" + " " + file
        print(cmd)
        process = os.popen(cmd)


class ImportConfigCommand(sublime_plugin.WindowCommand):
    def run(self):
        cmd1 = "cd " + FOLDER
        cmd = cmd1 + " && " + "java " + "FileSelector"
        print(cmd)
        process = os.popen(cmd)
        result = process.read()
        result = result.encode('ascii', 'ignore').decode('ascii')
        result = re.split(r'\s{2,}', result)
        file_path = os.path.join(FOLDER, "config_file.txt")
        file = open(file_path, "w")
        file.flush()
        file.write(result[0])


class ResetConfigCommand(sublime_plugin.WindowCommand):
    def run(self):
        file_path = os.path.join(FOLDER, "config_file.txt")
        file = open(file_path, "w")
        file.flush()
        TEMP_CONFIG_FILE = ""


class CreateRuleCommand(sublime_plugin.WindowCommand):
    def run(self):
        cmd1 = "cd " + FOLDER
        cmd = cmd1 + " && " + "java -jar " + "RuleImport.jar"
        process = os.popen(cmd)
        result = process.read()
        if result is not "":
            result = result.encode('ascii', 'ignore').decode('ascii')
            file_name = os.path.basename(result)
            test_file = result + "test.js"
            self.window.open_file(os.path.join(result, file_name + ".js"))
            self.window.open_file(os.path.join(result, test_file))


class ImportAndTestRuleCommand(EslintCommand):
    def run(self):
        self.init()
        cmd1 = "cd " + FOLDER
        cmd = cmd1 + " && " + "java " + "FileSelector" + " Test"

        process = os.popen(cmd)
        result = process.read()
        file_name = result.encode('ascii', 'ignore').decode('ascii')
        folder_name = os.path.dirname(file_name)
        file_path = os.path.join(FOLDER, "current_test_rule.txt")
        file = open(file_path, "w")
        file.flush()
        file.write(file_name)
        file_name = '"' + file_name + '"'

        cmd = 'eslint ' + self.s.get('node_eslint_options',
                                     '') + ' "' + self.file_path + '"' + " --rulesdir " + '"' + folder_name + '"' + " -c " + file_name
        print(cmd)
        AsyncProcess(cmd, self)
        StatusProcess('Starting ESLint for file ' + self.file_name, self)
        EsLintEventListener.disabled = True


class TestRuleCommand(EslintCommand):
    def run(self):
        self.init()
        current_test_file = getCurrentTestRule()

        if current_test_file:
            file_name = current_test_file
        else:
            cmd1 = "cd " + FOLDER
            cmd = cmd1 + " && " + "java " + "FileSelector" + " Test"
            process = os.popen(cmd)
            result = process.read()
            file_name = result.encode('ascii', 'ignore').decode('ascii')

        folder_name = os.path.dirname(file_name)
        file_name = '"' + file_name + '"'

        cmd = 'eslint ' + self.s.get('node_eslint_options',
                                     '') + ' "' + self.file_path + '"' + " --rulesdir " + '"' + folder_name + '"' + " -c " + file_name

        AsyncProcess(cmd, self)
        StatusProcess('Starting ESLint for file ' + self.file_name, self)
        EsLintEventListener.disabled = True


class ImportRuleCommand(sublime_plugin.WindowCommand):
    def run(self):
        eslint_lib_path = os.path.join(FOLDER, "custom_rules")

        cmd1 = "cd " + FOLDER
        cmd = cmd1 + " && " + "java " + "FileSelector" + " Test " + "1"
        print(cmd)
        process = os.popen(cmd)
        result = process.read()
        custom_rule_file = result.encode('ascii', 'ignore').decode('ascii')
        custom_rule_folder = os.path.dirname(custom_rule_file)

        file_name = os.path.basename(custom_rule_file)
        rule_name = file_name.replace(".js", "")
        json_file = file_name.replace(".js", "metadata.json")
        json_file = os.path.join(custom_rule_folder, json_file)

        copy2(custom_rule_file, eslint_lib_path)
        #
        dest_json_file = os.path.join(FOLDER, "JSON", "CustomRules.json")
        #
        with open(json_file) as data_file:
            data = json.load(data_file)

        with open(dest_json_file) as dest_data_file:
            prev_data = json.load(dest_data_file)

        flag = 0
        for data1 in prev_data:
            if data1["Name"] == data["Name"]:
                flag = 1
                break

        if flag is not 1:
            prev_data.append(data)
            with open(dest_json_file, mode='w') as dest_data_file:
                dest_data_file.write(json.dumps(prev_data, indent=2))
                global_json_file = os.path.join(FOLDER, "global.json")

                with open(global_json_file) as rule_data_file:
                    rule_data = json.load(rule_data_file)
                    rule_data["rules"][rule_name] = "error"

                with open(global_json_file, mode='w') as global_json_file:
                    global_json_file.write(json.dumps(rule_data, indent=2))
        else:
            print("Double data found")
