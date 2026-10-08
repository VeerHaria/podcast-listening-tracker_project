"""Tkinter window with three tabs: Podcasts, Episodes, Analysis."""
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

import analysis
import charts
import storage
import validation as v


def labeled(parent, text, widget, variable, **options):
    """Put a label and an input box side by side."""
    ttk.Label(parent, text=text).pack(side="left", padx=(8, 2))
    box = widget(parent, textvariable=variable, **options)
    box.pack(side="left", padx=(0, 6))
    return box


def make_tree(parent, columns, widths):
    tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
    for name, width in zip(columns, widths):
        tree.heading(name, text=name.title())
        tree.column(name, width=width)
    tree.pack(fill="both", expand=True, padx=8, pady=8)
    return tree


def fill_tree(tree, table):
    """Show a table in a Treeview. The row number is used as the row id."""
    tree.delete(*tree.get_children())
    for index, row in table.iterrows():
        tree.insert("", "end", iid=str(index), values=list(row))


class App(tk.Tk):
    def __init__(self, podcasts, episodes):
        super().__init__()
        self.title("Podcast Listening Tracker")
        self.geometry("1000x600")
        self.podcasts, self.episodes = podcasts, episodes
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", background="#2F4B66", foreground="white", padding=6)
        style.map("TButton", background=[("active", "#243A50")])

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=8, pady=8)
        self.build_podcast_tab(tabs)
        self.build_episode_tab(tabs)
        self.build_analysis_tab(tabs)
        self.refresh()

    # ---------- build screens ----------
    def build_podcast_tab(self, tabs):
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Podcasts")
        form = ttk.Frame(tab)
        form.pack(fill="x", pady=8)
        self.p_name, self.p_cat = tk.StringVar(), tk.StringVar()
        labeled(form, "Name", ttk.Entry, self.p_name, width=30)
        labeled(form, "Category", ttk.Combobox, self.p_cat, values=v.CATEGORIES,
                state="readonly", width=14)
        ttk.Button(form, text="Add podcast", command=self.add_podcast).pack(side="left", padx=4)
        ttk.Button(form, text="Delete selected", command=self.delete_podcast).pack(side="left")
        self.p_tree = make_tree(tab, ["podcast", "category"], [400, 200])

    def build_episode_tab(self, tabs):
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Episodes")
        self.e_vars = {k: tk.StringVar() for k in ("podcast", "title", "date", "minutes", "rating")}
        form = ttk.Frame(tab)
        form.pack(fill="x", pady=(8, 0))
        self.e_podcast_box = labeled(form, "Podcast", ttk.Combobox, self.e_vars["podcast"],
                                     state="readonly", width=18)
        labeled(form, "Title", ttk.Entry, self.e_vars["title"], width=22)
        labeled(form, "Date", ttk.Entry, self.e_vars["date"], width=11)
        labeled(form, "Minutes", ttk.Entry, self.e_vars["minutes"], width=6)
        labeled(form, "Rating", ttk.Combobox, self.e_vars["rating"],
                values=["1", "2", "3", "4", "5"], state="readonly", width=3)
        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=6)
        for text, command in (("Add", self.add_episode), ("Update selected", self.update_episode),
                              ("Delete selected", self.delete_episode)):
            ttk.Button(buttons, text=text, command=command).pack(side="left", padx=(8, 0))

        search = ttk.Frame(tab)
        search.pack(fill="x")
        self.search_text, self.search_rating = tk.StringVar(), tk.StringVar(value="Any")
        labeled(search, "Search", ttk.Entry, self.search_text, width=24)
        labeled(search, "Minimum rating", ttk.Combobox, self.search_rating,
                values=["Any", "1", "2", "3", "4", "5"], state="readonly", width=5)
        ttk.Button(search, text="Search", command=self.show_episodes).pack(side="left", padx=4)
        ttk.Button(search, text="Show all", command=self.clear_search).pack(side="left")

        self.e_tree = make_tree(tab, ["podcast", "title", "date", "minutes", "rating"],
                                [180, 300, 100, 70, 60])
        self.e_tree.bind("<<TreeviewSelect>>", self.fill_form)

    def build_analysis_tab(self, tabs):
        tab = ttk.Frame(tabs)
        tabs.add(tab, text="Analysis")
        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Show report", command=self.show_report).pack(side="left", padx=8)
        for name, func in charts.CHARTS.items():
            ttk.Button(buttons, text=name.replace("_", " ").title(),
                       command=lambda f=func: self.show_chart(f)).pack(side="left", padx=4)
        ttk.Button(buttons, text="Save charts", command=self.save_charts).pack(side="left", padx=8)
        self.report_box = tk.Text(tab, font="TkFixedFont", state="disabled")
        self.report_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    # ---------- show data ----------
    def refresh(self):
        fill_tree(self.p_tree, self.podcasts)
        self.e_podcast_box["values"] = list(self.podcasts["podcast"])
        self.show_episodes()

    def show_episodes(self):
        table = self.episodes
        text = self.search_text.get().strip().lower()
        if text:
            match = (table["title"].str.lower().str.contains(text, regex=False)
                     | table["podcast"].str.lower().str.contains(text, regex=False))
            table = table[match]
        if self.search_rating.get() != "Any":
            table = table[pd.to_numeric(table["rating"]) >= int(self.search_rating.get())]
        fill_tree(self.e_tree, table.sort_values("date", ascending=False))

    def clear_search(self):
        self.search_text.set("")
        self.search_rating.set("Any")
        self.show_episodes()

    def fill_form(self, _event=None):
        selected = self.e_tree.selection()
        if selected:
            row = self.episodes.loc[int(selected[0])]
            for name, var in self.e_vars.items():
                var.set(str(row[name]))

    # ---------- save helpers ----------
    def save(self):
        try:
            storage.save_all(self.podcasts, self.episodes)
        except OSError as error:
            messagebox.showerror("File error", f"Could not save: {error}")

    def run(self, action):
        """Run an action. Show a message if the input is invalid."""
        try:
            action()
        except ValueError as error:
            messagebox.showwarning("Invalid input", str(error))

    # ---------- podcast actions ----------
    def add_podcast(self):
        def action():
            name = v.check_text(self.p_name.get(), "Podcast name")
            category = v.check_category(self.p_cat.get())
            if name.lower() in self.podcasts["podcast"].str.lower().values:
                raise ValueError("This podcast already exists.")
            self.podcasts.loc[len(self.podcasts)] = [name, category]
            self.p_name.set("")
            self.save()
            self.refresh()
        self.run(action)

    def delete_podcast(self):
        def action():
            selected = self.p_tree.selection()
            if not selected:
                raise ValueError("Select a podcast first.")
            name = self.podcasts.loc[int(selected[0]), "podcast"]
            if messagebox.askyesno("Confirm", f"Delete {name} and all its episodes?"):
                self.podcasts = self.podcasts.drop(int(selected[0])).reset_index(drop=True)
                self.episodes = self.episodes[self.episodes["podcast"] != name].reset_index(drop=True)
                self.save()
                self.refresh()
        self.run(action)

    # ---------- episode actions ----------
    def read_form(self, skip_row=None):
        """Check every field and return one clean row."""
        podcast = self.e_vars["podcast"].get()
        if podcast not in list(self.podcasts["podcast"]):
            raise ValueError("Choose a podcast.")
        title = v.check_text(self.e_vars["title"].get(), "Episode title")
        day = v.check_date(self.e_vars["date"].get())
        minutes = v.check_number(self.e_vars["minutes"].get(), "Minutes", 1, 600)
        rating = v.check_number(self.e_vars["rating"].get(), "Rating", 1, 5)
        same = ((self.episodes["podcast"] == podcast) & (self.episodes["title"] == title)
                & (self.episodes["date"] == day))
        if skip_row is not None:
            same = same.drop(skip_row)       # ignore the row being updated
        if same.any():
            raise ValueError("This episode is already recorded for that date.")
        return [podcast, title, day, minutes, rating]

    def selected_row(self):
        selected = self.e_tree.selection()
        if not selected:
            raise ValueError("Select an episode first.")
        return int(selected[0])

    def add_episode(self):
        def action():
            self.episodes.loc[len(self.episodes)] = self.read_form()
            self.save()
            self.refresh()
        self.run(action)

    def update_episode(self):
        def action():
            row = self.selected_row()
            self.episodes.loc[row] = self.read_form(skip_row=row)
            self.save()
            self.refresh()
        self.run(action)

    def delete_episode(self):
        def action():
            row = self.selected_row()
            if messagebox.askyesno("Confirm", "Delete this episode?"):
                self.episodes = self.episodes.drop(row).reset_index(drop=True)
                self.save()
                self.refresh()
        self.run(action)

    # ---------- analysis actions ----------
    def get_data(self):
        if self.episodes.empty:
            messagebox.showinfo("No data", "Add some episodes first.")
            return None
        return analysis.prepare(self.episodes, self.podcasts)

    def show_report(self):
        df = self.get_data()
        if df is not None:
            self.report_box.configure(state="normal")
            self.report_box.delete("1.0", "end")
            self.report_box.insert("1.0", analysis.report(df))
            self.report_box.configure(state="disabled")

    def show_chart(self, chart_function):
        df = self.get_data()
        if df is not None:
            window = tk.Toplevel(self)
            canvas = FigureCanvasTkAgg(chart_function(df), master=window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    def save_charts(self):
        df = self.get_data()
        if df is not None:
            try:
                for name, func in charts.CHARTS.items():
                    func(df).savefig(storage.DATA.parent / "reports" / f"{name}.png", dpi=120)
                messagebox.showinfo("Saved", "Charts saved in the reports folder.")
            except OSError as error:
                messagebox.showerror("File error", f"Could not save: {error}")
