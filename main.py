import flet as ft
import sqlite3
import os

# 1. SQL Database Initialization
def init_db():
    db_dir = os.environ.get("FLET_APP_DATA", ".")
    db_path = os.path.join(db_dir, "My.db")

    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, Amount REAL, Note TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS earnings (id INTEGER PRIMARY KEY AUTOINCREMENT, Amount REAL, Note TEXT)")
    conn.commit()
    return conn

# ------------------------ UI ------------------------
def main(page: ft.Page):
    page.title = "Every Penny"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    conn = init_db()
    body_container = ft.Container(expand=True)

    # 1. Build the DataTable from SQLite rows
    def get_expenses_table():
        cursor = conn.cursor()
        cursor.execute("SELECT id, Note, Amount FROM expenses ORDER BY id DESC")
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
                                f"- ₹{row[2]:,.2f}",
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
    # 2. Home Dashboard Screen
    def show_home(e=None):
        body_container.content = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Expense Ledger", size=22, weight=ft.Colors.RED_400),
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
                if amt <= 0 or not desc:
                    status_text.value = "Enter a valid amount and note."
                    status_text.color = ft.Colors.RED_400
                    page.update()
                    return

                cursor = conn.cursor()
                cursor.execute("INSERT INTO expenses (Amount, Note) VALUES (?, ?)", (amt, desc))
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