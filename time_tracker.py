import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_FILE = "time_tracker_data.json"

# Load data from file
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save data to file
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

# Initialize data
items = load_data()

# Helper functions
def fetch_items():
    return [(name, data['last_recorded']) for name, data in items.items()]

def add_item(name):
    if name in items:
        return False
    items[name] = {'last_recorded': "未记录", 'records': []}
    save_data()
    return True

def edit_item(old_name, new_name):
    if new_name in items and old_name != new_name:
        return False
    items[new_name] = items.pop(old_name)
    save_data()
    return True

def delete_item(name):
    if name in items:
        del items[name]
        save_data()
        return True
    return False

def add_record_to_item(name, record_time):
    if name in items:
        items[name]['records'].append(record_time)
        items[name]['records'].sort()
        items[name]['last_recorded'] = record_time
        save_data()
        return True
    return False

def fetch_records(name):
    if name in items:
        return items[name]['records']
    return []

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("时间跟踪器  V2025.01.01 By vipnetant")

        self.create_widgets()

    def create_widgets(self):
        self.title_label = ttk.Label(self.root, text="时间跟踪器", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.item_frame = ttk.Frame(self.root)
        self.item_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.item_tree = ttk.Treeview(self.item_frame, columns=("序号", "名称", "最后记录时间"), show="headings", height=10)
        self.item_tree.heading("序号", text="序号")
        self.item_tree.heading("名称", text="名称")
        self.item_tree.heading("最后记录时间", text="最后记录时间")

        self.item_tree.column("序号", width=50, anchor="center")
        self.item_tree.column("名称", width=150, anchor="center")
        self.item_tree.column("最后记录时间", width=200, anchor="center")

        self.item_tree.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.item_frame, orient="vertical", command=self.item_tree.yview)
        self.item_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)

        self.add_item_button = ttk.Button(self.button_frame, text="添加项目", command=self.add_item_prompt)
        self.add_item_button.grid(row=0, column=0, padx=5)

        self.edit_item_button = ttk.Button(self.button_frame, text="编辑项目", command=self.edit_item_prompt)
        self.edit_item_button.grid(row=0, column=1, padx=5)

        self.delete_item_button = ttk.Button(self.button_frame, text="删除项目", command=self.delete_item_prompt)
        self.delete_item_button.grid(row=0, column=2, padx=5)

        self.refresh_button = ttk.Button(self.button_frame, text="刷新", command=self.refresh_items)
        self.refresh_button.grid(row=0, column=3, padx=5)

        self.item_tree.bind("<Double-1>", self.open_item_details)
        self.refresh_items()

    def refresh_items(self):
        for row in self.item_tree.get_children():
            self.item_tree.delete(row)
        items_list = fetch_items()
        for idx, item in enumerate(items_list, start=1):
            self.item_tree.insert("", "end", values=(idx, item[0], item[1]))

    def add_item_prompt(self):
        name = simpledialog.askstring("添加项目", "请输入项目名称：")
        if name:
            if add_item(name):
                self.refresh_items()
            else:
                messagebox.showerror("错误", "项目名称已存在！")

    def edit_item_prompt(self):
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个项目！")
            return

        old_name = self.item_tree.item(selected[0], "values")[1]
        new_name = simpledialog.askstring("编辑项目", "请输入新的项目名称：", initialvalue=old_name)
        if new_name and new_name != old_name:
            if edit_item(old_name, new_name):
                self.refresh_items()
            else:
                messagebox.showerror("错误", "项目名称已存在！")

    def delete_item_prompt(self):
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个项目！")
            return

        name = self.item_tree.item(selected[0], "values")[1]
        if messagebox.askyesno("确认删除", f"确定要删除项目 '{name}' 吗？"):
            if delete_item(name):
                self.refresh_items()

    def open_item_details(self, event):
        selected = self.item_tree.selection()
        if not selected:
            return

        name = self.item_tree.item(selected[0], "values")[1]
        records = fetch_records(name)

        top = tk.Toplevel(self.root)
        top.title(f"{name} - 记录详情")

        record_frame = ttk.Frame(top)
        record_frame.pack(fill="both", expand=True, padx=10, pady=10)

        record_tree = ttk.Treeview(record_frame, columns=("序号", "时间点"), show="headings", height=10)
        record_tree.heading("序号", text="序号")
        record_tree.heading("时间点", text="时间点")
        record_tree.column("序号", width=50, anchor="center")
        record_tree.column("时间点", width=200, anchor="center")
        record_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(record_frame, orient="vertical", command=record_tree.yview)
        record_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def refresh_records():
            for row in record_tree.get_children():
                record_tree.delete(row)
            for idx, record in enumerate(records, start=1):
                record_tree.insert("", "end", values=(idx, record))

        refresh_records()

        button_frame = ttk.Frame(top)
        button_frame.pack(pady=10)

        def add_record():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if add_record_to_item(name, now):
                refresh_records()
                self.refresh_items()  # Refresh the main window to update the last recorded time
                messagebox.showinfo("成功", f"已为项目 '{name}' 添加记录：{now}")

        def edit_record():
            selected_record = record_tree.selection()
            if not selected_record:
                messagebox.showwarning("警告", "请选择一个记录！")
                return
            old_record = record_tree.item(selected_record[0], "values")[1]
            new_record = simpledialog.askstring("编辑记录", "请输入新的记录时间 (格式: YYYY-MM-DD HH:MM:SS)：", initialvalue=old_record)
            try:
                if new_record and datetime.strptime(new_record, "%Y-%m-%d %H:%M:%S"):
                    records.remove(old_record)
                    records.append(new_record)
                    records.sort()
                    items[name]['records'] = records
                    items[name]['last_recorded'] = records[-1]
                    save_data()
                    refresh_records()
                    self.refresh_items()  # Refresh the main window to update the last recorded time
                    messagebox.showinfo("成功", f"记录已更新为：{new_record}")
            except ValueError:
                messagebox.showerror("错误", "时间格式不正确！请使用 YYYY-MM-DD HH:MM:SS 格式。")

        def delete_record():
            selected_record = record_tree.selection()
            if not selected_record:
                messagebox.showwarning("警告", "请选择一个记录！")
                return
            record = record_tree.item(selected_record[0], "values")[1]
            if messagebox.askyesno("确认删除", f"确定要删除记录 '{record}' 吗？"):
                records.remove(record)
                if records:
                    items[name]['last_recorded'] = records[-1]
                else:
                    items[name]['last_recorded'] = "未记录"
                items[name]['records'] = records
                save_data()
                refresh_records()
                self.refresh_items()  # Refresh the main window to update the last recorded time

        add_button = ttk.Button(button_frame, text="添加记录", command=add_record)
        add_button.grid(row=0, column=0, padx=5)

        edit_button = ttk.Button(button_frame, text="编辑记录", command=edit_record)
        edit_button.grid(row=0, column=1, padx=5)

        delete_button = ttk.Button(button_frame, text="删除记录", command=delete_record)
        delete_button.grid(row=0, column=2, padx=5)

        def view_chart():
            if not records:
                messagebox.showwarning("无记录", f"项目 '{name}' 暂无记录，无法生成图表！")
                return

            chart_top = tk.Toplevel(top)
            chart_top.title(f"{name} - 时间记录图")

            fig, ax = plt.subplots()
            fig.suptitle(f"{name} - 时间记录图", fontproperties="SimHei")

            dates = [datetime.strptime(record, "%Y-%m-%d %H:%M:%S") for record in records]
            ax.plot_date(date2num(dates), range(1, len(dates) + 1), linestyle="solid", marker="o")

            ax.set_xlabel("日期", fontproperties="SimHei")
            ax.set_ylabel("次数", fontproperties="SimHei")
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=chart_top)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        view_chart_button = ttk.Button(button_frame, text="查看图表", command=view_chart)
        view_chart_button.grid(row=0, column=3, padx=5)

# Main entry
if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
