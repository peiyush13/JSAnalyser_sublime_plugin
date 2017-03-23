import os
import re
import sublime
import sublime_plugin

try:
    from edit_buffer import *
    from statusprocess import *
    from asyncprocess import *
except ImportError:
    from .edit_buffer import *
    from .statusprocess import *
    from .asyncprocess import *

RESULT_VIEW_NAME = 'eslint_result_view'
SETTINGS_FILE = "sublime-eslint.sublime-settings"


class ShowEslintResultCommand(sublime_plugin.WindowCommand):
    """show jslint result"""

    def run(self):
        self.window.run_command("show_panel", {"panel": "output." + RESULT_VIEW_NAME})


class JslintCommand(sublime_plugin.WindowCommand):
    def run(self):
        s = sublime.load_settings(SETTINGS_FILE)

        file_path = self.window.active_view().file_name()
        file_name = os.path.basename(file_path)
        self.debug = s.get('debug', False)
        self.buffered_data = ''
        self.file_path = file_path
        self.file_name = file_name
        self.is_running = True
        self.tests_panel_showed = False
        self.ignored_error_count = 0
        self.ignore_errors = s.get('ignore_errors', [])
        self.use_node_eslint = s.get('use_node_eslint', True)

        self.init_tests_panel()

        cmd = 'eslint ' + s.get('node_eslint_options', '') + ' "' + file_path + '"'

        AsyncProcess(cmd, self)
        StatusProcess('Starting ESLint for file ' + file_name, self)

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

    def append_data(self, proc, bData, end=False):
        if self.debug:
            print("DEBUG: append_data start")
        data = bData.decode('utf-8')
        data = re.split(r'\s{2,}', data)
        count = 0
        data[count]+="\n"
        while count < len(data)-2:

            if count % 4 == 0:
                data[count]+="\n"

            if (count+1)%4==0:
                data[count]+="\t"

            if (count+2)%4==0:
                data[count]+="\t"

            if (count + 3) % 4 == 0:
                temp=list(data[count])
                temp[0]=" Line No=> "+temp[0]
                temp[2]= " Position=> "+ temp[2]+ " "
                data[count]="".join(temp)

            count += 1

        data=" ".join(data)

        self.show_tests_panel()

        with Edit(self.output_view, True) as edit:
            edit.insert(self.output_view.size(), str(data))



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
    """jslint event"""
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

        # run jslint.
        sublime.active_window().run_command("jslint")

    def on_deactivated(self, view):
        if view.name() != RESULT_VIEW_NAME:
            return
        self.previous_resion = None

        if self.file_view:
            self.file_view.erase_regions(RESULT_VIEW_NAME)

            # def on_selection_modified(self, view):
            #     if EsLintEventListener.disabled:
            #         return
            #     if view.name() != RESULT_VIEW_NAME:
            #         return
            #     region = view.line(view.sel()[0])
            #     s = sublime.load_settings(SETTINGS_FILE)
            #
            #     # make sure call once.
            #     if self.previous_resion == region:
            #         return
            #     self.previous_resion = region
            #
            #     # extract line from jslint result.
            #     if (s.get('use_node_eslint', False)):
            #         pattern_position = "\\/\\/ Line (\d+), Pos (\d+)$"
            #         text = view.substr(region)
            #         text = re.findall(pattern_position, text)
            #         if len(text) > 0:
            #             line = int(text[0][0])
            #             col = int(text[0][1])
            #     else:
            #         text = view.substr(region).split(':')
            #         if len(text) < 4 or text[0] != 'jslint' or re.match('\d+', text[2]) is None or re.match('\d+', text[3]) is None:
            #                 return
            #         line = int(text[2])
            #         col = int(text[3])
            #
            #     # hightligh view line.
            #     view.add_regions(RESULT_VIEW_NAME, [region], "comment")
            #
            #     # find the file view.
            #     file_path = view.settings().get('file_path')
            #     window = sublime.active_window()
            #     file_view = None
            #     for v in window.views():
            #         if v.file_name() == file_path:
            #             file_view = v
            #             break
            #     if file_view is None:
            #         return
            #
            #     self.file_view = file_view
            #     window.focus_view(file_view)
            #     file_view.run_command("goto_line", {"line": line})
            #     file_region = file_view.line(file_view.sel()[0])
            #
            #     # highlight file_view line
            #     file_view.add_regions(RESULT_VIEW_NAME, [file_region], "string")
