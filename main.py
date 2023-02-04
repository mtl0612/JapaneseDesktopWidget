import os
import time
import random
import configparser
import tkinter as tk
from tkinter import simpledialog
from tkinter import colorchooser
import textwrap

debug = False
config_file = "vocabulary.ini"


bg_color = "#121212"


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.configure(bg=bg_color)
        self.pack(fill="both", expand="True")

        self.word_index = -1
        self.last_changed_time = None
        self.labels = []

        self.on_top = tk.BooleanVar()

        self.auto_next = tk.BooleanVar()
        self.auto_next.set(True)

        self.window_border_visibility = tk.BooleanVar()
        self.window_border_visibility.set(False)

        self.transparent = tk.BooleanVar()
        self.transparent.set(True)

        self.viet_labels_visibility = False
        self.vocab_labels_visibility = True

        self.toggleShowHideWindowBorder()
        self.createWidgets()
        self.loadConfig()
        self.createMenu()

        self.vocabulary_text = self.loadData(self.data_file)

        if self.shuffle:
            self.shuffle_words()

        self.setVietLabelsVisibility(self.viet_labels_visibility)

        if debug:
            self.master.geometry(
                f"{self.window_width}x{self.window_height+40}+{self.window_x}+{self.window_y}"
            )
        else:
            self.master.geometry(
                f"{self.window_width}x{self.window_height+40}+{self.window_x}+{self.window_y}"
            )

        self.master.bind("<space>", self.toggleVietLabels)
        self.master.bind("<Control-k>", self.toggleVocabLabels)
        self.master.bind("<Left>", self.prev_vocab_word)
        self.master.bind("<Right>", self.on_btn_next)

        self.saveConfig()

    def loadConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read_dict(
            {
                "DEFAULT": {
                    "shuffle": "False",
                    "alway_on_top": "False",
                    "data_file": "tuvungn3.txt",
                    "change_interval": 1,
                    "delay_in_s": 0.5,
                },
                "GEOMETRY": {
                    "window_width": "300",
                    "window_height": "200",
                    "window_x": "800",
                    "window_y": "10",
                },
            }
        )
        self.config.read(config_file)

        self.window_width = self.config.getint("GEOMETRY", "window_width")
        self.window_height = self.config.getint("GEOMETRY", "window_height")
        self.window_x = self.config.getint("GEOMETRY", "window_x")
        self.window_y = self.config.getint("GEOMETRY", "window_y")
        self.shuffle = self.config.getboolean("GEOMETRY", "shuffle")
        self.on_top.set(self.config.getboolean("GEOMETRY", "shuffle"))
        self.data_file = self.config["DEFAULT"]["data_file"]
        self.change_interval = self.config.getfloat("DEFAULT", "delay_in_s")
        self.delay_in_s = self.config.getfloat("DEFAULT", "delay_in_s")

        self.setAlwaysOnTop(self.on_top.get())

    def saveConfig(self):
        with open(config_file, "w") as f:
            self.config.write(f)

    def loadData(self, data_file):
        with open(data_file, "r", encoding="utf-8-sig") as f:
            data = f.read().splitlines()
        data = [item.split("|") for item in data]
        return data

    def createWidgets(self):
        self.lbl_number = tk.Label(self, fg="white", bg="black")
        self.lbl_number["text"] = ""
        self.lbl_number.pack(side="top", pady="5 0")
        self.lbl_number.configure(font=("MS Gothic", 12, "normal"))
        self.bindWidgetToMoveFunction(self.lbl_number)
        self.labels.append(self.lbl_number)

        self.lbl_hiragana = tk.Label(self, fg="white", bg="black")
        self.lbl_hiragana["text"] = ""
        self.lbl_hiragana.pack(side="top", pady="5 0")
        self.lbl_hiragana.configure(font=("BIZ UDMincho", 25, "normal"))
        self.bindWidgetToMoveFunction(self.lbl_hiragana)
        self.labels.append(self.lbl_hiragana)

        self.frm_vocab = tk.Frame(self, bg=bg_color)
        self.frm_vocab.pack(side="top")

        self.lbl_previous = tk.Label(self.frm_vocab, fg="white", bg="black")
        self.lbl_previous["text"] = "◀"
        self.lbl_previous.grid(row=0, column=0, sticky=tk.W, padx="0 20")
        self.lbl_previous.configure(font=("MS Gothic", 30, "normal"))
        self.lbl_previous.bind("<Button-1>", self.prev_vocab_word)
        self.labels.append(self.lbl_previous)

        self.lbl_vocabulary = tk.Label(self.frm_vocab, fg="white", bg="black")
        self.lbl_vocabulary["text"] = ""
        self.lbl_vocabulary.grid(row=0, column=1, sticky=tk.EW)
        self.lbl_vocabulary.configure(font=("BIZ UDMincho", 30, "normal"))
        self.bindWidgetToMoveFunction(self.lbl_vocabulary)
        self.labels.append(self.lbl_vocabulary)

        self.lbl_next = tk.Label(self.frm_vocab, fg="white", bg="black")
        self.lbl_next["text"] = "▶"
        self.lbl_next.grid(row=0, column=2, sticky=tk.E, padx="20 0")
        self.lbl_next.configure(font=("MS Gothic", 30, "normal"))
        self.lbl_next.bind("<Button-1>", lambda x: self.next_vocab_word(force=True))
        self.labels.append(self.lbl_next)

        self.lbl_meaning = tk.Label(self, fg="white", bg="black")
        self.lbl_meaning["text"] = ""
        self.lbl_meaning.pack(side="top", pady="5 0")
        self.lbl_meaning.configure(font=("Microsoft YaHei", 14, "normal"))
        self.bindWidgetToMoveFunction(self.lbl_meaning)
        self.labels.append(self.lbl_meaning)

    def createMenu(self):
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="Shuffle words", command=self.shuffle_words)
        m.add_checkbutton(
            label="Auto next", onvalue=1, offvalue=0, variable=self.auto_next
        )
        m.add_separator()
        m.add_command(label="Next word", command=self.next_vocab_word)
        m.add_command(label="Go to ...", command=self.goto_vocab_word)
        m.add_command(label="Restart", command=self.restart)
        m.add_separator()
        m.add_command(
            label="Copy furigana to clipboard", command=self.copy_furigana_to_clipboard
        )
        m.add_command(
            label="Copy word to clipboard", command=self.copy_word_to_clipboard
        )
        m.add_separator()
        m.add_command(label="Change text color...", command=self.change_text_color)
        m.add_checkbutton(
            label="Show window border",
            onvalue=True,
            offvalue=False,
            variable=self.window_border_visibility,
            command=self.toggleShowHideWindowBorder,
        )
        m.add_checkbutton(
            label="Transparent",
            onvalue=True,
            offvalue=False,
            variable=self.transparent,
            command=self.toggleShowHideWindowBorder,
        )
        m.add_checkbutton(
            label="Always on Top",
            onvalue=True,
            offvalue=False,
            variable=self.on_top,
            command=self.toggleAlwaysOnTop,
        )
        m.add_separator()
        m.add_command(label="Exit", command=root.destroy)

        def do_popup(event):
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()

        self.bind("<Button-3>", do_popup)
        for lbl in self.labels:
            lbl.bind("<Button-3>", do_popup)

    def restart(self):
        self.word_index = -1
        self.next_vocab_word(force=True)

    def goto_vocab_word(self):
        new_index = simpledialog.askinteger(
            "Input index", "Please input index", parent=self
        )
        if new_index <= len(self.vocabulary_text):
            self.word_index = new_index - 2
            self.next_vocab_word(force=True)

    def setLabelsText(self, entry):
        self.lbl_number["text"] = f"{self.word_index+1}/{len(self.vocabulary_text)}"

        hiragana = "\n".join(textwrap.wrap(entry[1].strip(), width=7))
        self.lbl_hiragana["text"] = hiragana

        vocabulary = "\n".join(textwrap.wrap(entry[0].strip(), width=4))
        if vocabulary == "":
            vocabulary = hiragana
        self.lbl_vocabulary["text"] = vocabulary

        meaning = "\n".join(textwrap.wrap(entry[2].strip(), width=26))
        self.lbl_meaning["text"] = meaning

    def shuffle_words(self):
        random.shuffle(self.vocabulary_text)
        self.last_changed_time = None
        self.restart()

    def prev_vocab_word(self, event=None):
        self.word_index -= 1
        if self.word_index == -1:
            self.word_index = len(self.vocabulary_text) - 1
        vocab_word = self.vocabulary_text[self.word_index]
        self.setLabelsText(vocab_word)

    def on_btn_next(self, event=None):
        self.last_changed_time = None
        self.setVietLabelsVisibility(True)
        self.setVocabLabelsVisibility(True)
        self.after(
            int(self.delay_in_s * 1000),
            self.setVietLabelsVisibility,
            self.viet_labels_visibility,
        )
        self.after(
            int(self.delay_in_s * 1000),
            self.setVocabLabelsVisibility,
            self.vocab_labels_visibility,
        )
        self.after(int(self.delay_in_s * 1000) + 100, self.next_vocab_word)

    def next_vocab_word(self, event=None, force=False):
        # print("next_vocab_word called")
        if (
            not force
            and self.last_changed_time
            and (time.time() - self.last_changed_time) < (self.change_interval * 60)
        ):
            return

        self.word_index += 1
        if self.word_index == len(self.vocabulary_text):
            self.word_index = 0
        vocab_word = self.vocabulary_text[self.word_index]
        self.setLabelsText(vocab_word)
        self.last_changed_time = time.time()

    def auto_change_vocab_word(self):
        self.after(int(self.change_interval * 60 * 1000), self.auto_change_vocab_word)
        if self.last_changed_time and (time.time() - self.last_changed_time) < (
            self.change_interval * 60
        ):
            return
        if self.auto_next.get():
            self.next_vocab_word()

    def change_text_color(self):
        color_code = colorchooser.askcolor(title="Choose Font Color")[-1]
        for label in self.labels:
            label.configure(fg=color_code)

    def toggleVietLabels(self, *args):
        self.viet_labels_visibility = not self.viet_labels_visibility
        self.setVietLabelsVisibility(self.viet_labels_visibility)

    def toggleVocabLabels(self, *args):
        self.vocab_labels_visibility = not self.vocab_labels_visibility
        self.setVocabLabelsVisibility(self.vocab_labels_visibility)

    def setVietLabelsVisibility(self, show_flag):
        if show_flag:
            self.lbl_meaning.pack()
        else:
            self.lbl_meaning.pack_forget()

    def setVocabLabelsVisibility(self, show_flag):
        if show_flag:
            self.lbl_vocabulary.grid()
        else:
            self.lbl_vocabulary.grid_remove()

    def toggleShowHideWindowBorder(self):
        self.setTransparent(self.transparent.get())
        self.showWindowBorder(self.window_border_visibility.get())

    def showWindowBorder(self, show_flag):
        if show_flag:
            self.master.overrideredirect(0)
            self.master.wm_attributes("-transparentcolor", "")
            self.master.resizable(1, 1)
        else:
            self.master.overrideredirect(1)
            self.master.resizable(0, 0)
            

    def setTransparent(self, transparent):
        if not transparent:
            self.master.wm_attributes("-transparentcolor", "")
        else:
            self.master.wm_attributes("-transparentcolor", self["bg"])

    def toggleAlwaysOnTop(self):
        self.setAlwaysOnTop(self.on_top.get())

    def setAlwaysOnTop(self, on_top_flag):
        self.master.attributes("-topmost", on_top_flag)

    def copy_furigana_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append("".join(self.lbl_hiragana["text"].split("\n")))
        self.update()

    def copy_word_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append("".join(self.lbl_vocabulary["text"].split("\n")))
        self.update()

    def bindWidgetToMoveFunction(self, widget):
        widget.bind("<ButtonPress-1>", self.start_move)
        widget.bind("<ButtonRelease-1>", self.stop_move)
        widget.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.config["GEOMETRY"]["window_width"] = str(self.master.winfo_width())
        self.config["GEOMETRY"]["window_height"] = str(self.master.winfo_height())
        self.config["GEOMETRY"]["window_x"] = str(self.master.winfo_x())
        self.config["GEOMETRY"]["window_y"] = str(self.master.winfo_y())
        self.x = None
        self.y = None
        self.saveConfig()

    def do_move(self, event):
        try:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.master.winfo_x() + deltax
            y = self.master.winfo_y() + deltay
            self.master.geometry(f"+{x}+{y}")
        except AttributeError:
            pass


if __name__ == "__main__":
    print("Start....")
    root = tk.Tk()
    app = Application(master=root)
    app.after(100, app.auto_change_vocab_word)
    app.mainloop()
    print("End!")
