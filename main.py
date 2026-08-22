import flet as ft
import sqlite3
import os
from datetime import datetime

# 1. SQL Database Initialization
def init_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.environ.get("FLET_APP_DATA", base_dir)
    db_path = os.path.join(db_dir, "my.db")

    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, Date Text, Amount REAL, Note TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS earnings (id INTEGER PRIMARY KEY AUTOINCREMENT, Date Text, Amount REAL, Note TEXT)")
    conn.commit()
    return conn

# ------------------------ UI ------------------------
def main(page: ft.Page):
    page.title = "Every Penny"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    conn = init_db()
    body_container = ft.Container(expand=True)

    # 1. Build the DataTable from SQLite rows
    def get_expenses_table():
        cursor = conn.cursor()
        cursor.execute("SELECT id, Date, Note, Amount FROM expenses ORDER BY id DESC")
        records = cursor.fetchall()

        if not records:
            return ft.Text("No transactions logged yet.", size=16, color=ft.Colors.GREY_500)

        return ft.DataTable(
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Amount", weight=ft.FontWeight.BOLD), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"#{row[0]}")),
                        ft.DataCell(ft.Text(row[1])), # This renders the Date
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(
                            ft.Text(
                                f"- ₹{row[3]:,.2f}",
                                color=ft.Colors.RED_400,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                    ]
                )
                for row in records
            ],
        )
    # 5. Earning Table:
    def get_earnings_tables():
        cursor = conn.cursor()
        cursor.execute("SELECT id, Note, Amount FROM earnings ORDER BY id DESC")
        records = cursor.fetchall()

        if not records:
            return ft.Text("No transactions logged yet.", size=16, color=ft.Colors.GREY_500)

        return ft.DataTable(
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Amount", weight=ft.FontWeight.BOLD), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"#{row[0]}")),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(
                            ft.Text(
                                f"+ ₹{row[2]:,.2f}",
                                color=ft.Colors.GREEN_400,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                    ]
                )
                for row in records
            ],
        )
    #sql-qury total
    def get_total():
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(Amount) FROM expenses")
        row = cursor.fetchone()

        if row is None:
            return 0.0

        total = row[0]

        if total is None:
            return 0.0

        return float(total)
    
    # 7. Daily / Monthly summaries
    MONTH_NAMES = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
    }

    def get_daily_summary():
        # Sums Amount for every expense whose Date shares the same day-of-month (%d),
        # regardless of which month/year it fell in.
        cursor = conn.cursor()
        cursor.execute("SELECT Date, Amount FROM expenses")
        totals = {}
        for date_str, amount in cursor.fetchall():
            try:
                day = date_str.split("-")[0]
            except (AttributeError, IndexError):
                continue
            totals[day] = totals.get(day, 0.0) + amount
        return sorted(totals.items(), key=lambda item: int(item[0]))

    def get_monthly_summary():
        # Sums Amount for every expense whose Date shares the same month AND year
        # (%m-%Y), so August 2026 and August 2025 are kept separate.
        cursor = conn.cursor()
        cursor.execute("SELECT Date, Amount FROM expenses")
        totals = {}
        for date_str, amount in cursor.fetchall():
            try:
                _, month, year = date_str.split("-")
            except (AttributeError, ValueError):
                continue
            key = (year, month)
            totals[key] = totals.get(key, 0.0) + amount
        return sorted(totals.items(), key=lambda item: (item[0][0], item[0][1]))

    def build_summary_table(summary, label_col):
        if not summary:
            return ft.Text("No data yet.", size=16, color=ft.Colors.GREY_500)

        return ft.DataTable(
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            columns=[
                ft.DataColumn(ft.Text(label_col, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Total Spent", weight=ft.FontWeight.BOLD), numeric=True),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(key))),
                        ft.DataCell(
                            ft.Text(
                                f"- ₹{total:,.2f}",
                                color=ft.Colors.RED_400,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                    ]
                )
                for key, total in summary
            ],
        )

    def show_reports(e=None):
        daily_summary = get_daily_summary()
        monthly_summary = [
            (f"{MONTH_NAMES.get(month, month)} {year}", total)
            for (year, month), total in get_monthly_summary()
        ]

        body_container.content = ft.Column(
            controls=[
                ft.Text("Expense Reports", size=22, weight=ft.FontWeight.BOLD),
                ft.Tabs(
                    selected_index=0,
                    length=2,
                    animation_duration=300,
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            ft.TabBar(
                                tabs=[
                                    ft.Tab(label="Daily"),
                                    ft.Tab(label="Monthly"),
                                ],
                            ),
                            ft.TabBarView(
                                expand=True,
                                controls=[
                                    ft.Container(
                                        content=build_summary_table(daily_summary, "Day of Month"),
                                        padding=15,
                                    ),
                                    ft.Container(
                                        content=build_summary_table(monthly_summary, "Month"),
                                        padding=15,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.ElevatedButton("Back", icon=ft.Icons.ARROW_BACK, on_click=show_home),
            ],
            spacing=15,
        )
        page.update()

    # 2. Home Dashboard Screen
    def show_home(e=None):
        total_exp = get_total()

        body_container.content = ft.Column(
            controls=[
                #total exp display table
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(f"Total Expenses: - ₹{total_exp:,.2f}", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Expense Ledger", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                        ft.ElevatedButton(
                            "Log Expense",
                            icon=ft.Icons.ADD,
                            on_click=show_log,
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Earnings Ledger", size=22, weight=ft.Colors.GREEN_400),
                        ft.ElevatedButton(
                            "Log Earnings",
                            icon=ft.Icons.ADD,
                            on_click=show_earning,
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ElevatedButton(
                            "View Reports (Daily / Monthly)",
                            icon=ft.Icons.BAR_CHART,
                            on_click=show_reports,
                        ),
                    ],
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                # Render the DataTable inside a scrollable column
                ft.Column(
                    controls=[
                        get_expenses_table(),
                        get_earnings_tables()
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            spacing=15,
        )
        page.update()

    #6 Earnings
    def show_earning(e=None):
        amount_input = ft.TextField(
            label="Amount",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon="₹",
        )
        note_input_earning = ft.TextField(label="Note / Description")
        status_text = ft.Text("", size=14)

        def save_and_return(e):
            try:
                amt = float(amount_input.value)
                desc = note_input_earning.value.strip()
                if amt <= 0 or not desc:
                    status_text.value = "Enter a valid amount and note."
                    status_text.color = ft.Colors.RED_400
                    page.update()
                    return

                cursor = conn.cursor()
                cursor.execute("INSERT INTO earnings (Amount, Note) VALUES (?, ?)", (amt, desc))
                conn.commit()
                show_home()
            except (ValueError, TypeError):
                status_text.value = "Amount must be a valid number."
                status_text.color = ft.Colors.RED_400
                page.update()

        body_container.content = ft.Column(
            controls=[
                ft.Text("Log Earning", size=22, weight=ft.FontWeight.BOLD),
                amount_input,
                note_input_earning,
                status_text,
                ft.ElevatedButton("Save Entry", icon=ft.Icons.SAVE, on_click=save_and_return),
                ft.ElevatedButton("Cancel", icon=ft.Icons.ARROW_BACK, on_click=show_home),
            ],
            spacing=15
        )
        page.update()
       
    # 3. Manual Log Screen
    def show_log(e=None):
        amount_input = ft.TextField(
            label="Amount",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon="₹",
        )
        note_input = ft.TextField(label="Note / Description")
        status_text = ft.Text("", size=14)

        def save_and_return(e):
            try:
                amt = float(amount_input.value)
                desc = note_input.value.strip()
                current_date = datetime.now().strftime("%d-%m-%Y")
                if amt <= 0 or not desc:
                    status_text.value = "Enter a valid amount and note."
                    status_text.color = ft.Colors.RED_400
                    page.update()
                    return

                cursor = conn.cursor()
                cursor.execute("INSERT INTO expenses (Date, Amount, Note) VALUES (?, ?, ?)", (current_date, amt, desc))
                conn.commit()
                show_home()
            except (ValueError, TypeError):
                status_text.value = "Amount must be a valid number."
                status_text.color = ft.Colors.RED_400
                page.update()

        body_container.content = ft.Column(
            controls=[
                ft.Text("Log New Expense", size=22, weight=ft.FontWeight.BOLD),
                amount_input,
                note_input,
                status_text,
                ft.ElevatedButton("Save Entry", icon=ft.Icons.SAVE, on_click=save_and_return),
                ft.ElevatedButton("Cancel", icon=ft.Icons.ARROW_BACK, on_click=show_home),
            ],
            spacing=15,
        )
        page.update()

    # Base Layout
    page.add(
        ft.Text("Every Penny Counts - No cloud", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
        body_container,
    )

    # Initial Load
    show_home()

ft.app(target=main, view=ft.AppView.WEB_BROWSER)