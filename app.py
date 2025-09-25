# app.py
import os, sys, sqlite3, datetime
from PyQt6.QtCore import Qt, QDate, QTimer, QStringListModel
from PyQt6.QtGui import QIcon, QIntValidator
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout,
    QCheckBox, QListWidget, QListWidgetItem, QAbstractItemView, QTextEdit, QFormLayout,
    QScrollArea, QDateEdit, QMessageBox, QSpinBox, QStatusBar, QCompleter, QFrame, QRadioButton, QButtonGroup
)

DB_PATH = "journal.db"
DELIMS = [',', ';']

# ---------- DB helpers ----------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
    
def build_radio_group(options):  # options: list[(id, label)]
    box = QWidget()
    lay = QHBoxLayout(box); lay.setContentsMargins(0,0,0,0)
    group = QButtonGroup(box)
    for oid, label in options:
        rb = QRadioButton(label)
        rb.setProperty("opt_id", oid)
        lay.addWidget(rb)
        group.addButton(rb)
    lay.addStretch(1)
    return box, group

def get_selected_radio_id(group):
    b = group.checkedButton()
    return b.property("opt_id") if b else None

def fetchall(sql, params=()):
    with db() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()

def fetchone(sql, params=()):
    with db() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchone()

def exec_sql(sql, params=()):
    with db() as conn:
        conn.execute(sql, params)
        conn.commit()

def exec_many(sql, rows):
    with db() as conn:
        conn.executemany(sql, rows)
        conn.commit()

# Capitalize first letter of each word (basic Title Case, but keep small words as-is if user typed)
def smart_title(s: str) -> str:
    return " ".join(w[:1].upper() + w[1:] if w else "" for w in s.strip().split())

# ---------- Widgets ----------
class MultiSuggestLine(QLineEdit):
    """
    Comma/semicolon-separated input with top-3 DB suggestions for the CURRENT token.
    On completion, replaces only the active token. get_tokens() returns normalized list.
    """
    def __init__(self, table:str, column:str, limit:int=3, capitalize:bool=True):
        super().__init__()
        self.table = table
        self.column = column
        self.limit = limit
        self.capitalize = capitalize
        self.model = QStringListModel([])
        self.completer = QCompleter(self.model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated[str].connect(self.accept_completion)
        self.setCompleter(self.completer)
        self.textChanged.connect(self.requery)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

    def _split_tokens(self, text:str):
        # Split on commas/semicolons, strip spaces, drop empties
        raw = []
        token = ''
        for ch in text:
            if ch in DELIMS:
                raw.append(token)
                token = ''
            else:
                token += ch
        raw.append(token)
        tokens = [t.strip() for t in raw]
        return tokens

    def _join_tokens(self, tokens):
        # Re-join with ", " prettiness
        return ", ".join([t for t in tokens if t != ""])

    def _current_token_index(self):
        # We keep it simple: always use the LAST token for suggestions
        return len(self._split_tokens(self.text())) - 1

    def _norm(self, s:str):
        s = s.strip()
        if not s:
            return ""
        # Title-case like the rest of the app
        return " ".join(w[:1].upper() + w[1:] for w in s.split())

    def requery(self, _=None):
        tokens = self._split_tokens(self.text())
        if not tokens:
            self.model.setStringList([])
            return
        current = tokens[-1].strip()
        if not current:
            self.model.setStringList([])
            return

        # Fetch top-3 matching vibe names, excluding already chosen ones
        like = f"%{current}%"
        rows = fetchall(
            f"SELECT {self.column} FROM {self.table} "
            f"WHERE {self.column} LIKE ? "
            f"ORDER BY {self.column} LIMIT {self.limit}",
            (like,)
        )
        chosen = set(map(lambda x: x.lower(), [t for t in tokens[:-1] if t]))
        suggestions = [r[0] for r in rows if r[0].lower() not in chosen]
        self.model.setStringList(suggestions)
        if suggestions:
            self.completer.complete()


    def accept_completion(self, choice:str):
        tokens = self._split_tokens(self.text())
        if not tokens:
            tokens = [choice]
        else:
            tokens[-1] = choice
        # Normalize if needed
        if self.capitalize:
            tokens = [self._norm(t) for t in tokens]
        new_text = self._join_tokens(tokens)
        # add a trailing comma+space if not already there
        if not new_text.endswith(", "):
            new_text = new_text + ", "
        self.setText(new_text)
        self.setCursorPosition(len(new_text))


    def get_tokens(self):
        tokens = [self._norm(t) for t in self._split_tokens(self.text())]
        # dedupe, keep order
        seen = set()
        out = []
        for t in tokens:
            if t and t.lower() not in seen:
                seen.add(t.lower())
                out.append(t)
        return out

class NullableDateEdit(QDateEdit):
    def __init__(self):
        super().__init__()
        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy-MM-dd")
        self.setMinimumDate(QDate(1900,1,1))
        self.setSpecialValueText("—")   # shows as empty dash
        self.clear_to_null()

    def clear_to_null(self):
        self.setDate(self.minimumDate())

    def get_or_none(self):
        return None if self.date() == self.minimumDate() else self.date().toString("yyyy-MM-dd")

class DotRating(QWidget):
    """10-dot rating stored as 0..10; click to set. Later we can render as /5 via settings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.dots = []
        row = QHBoxLayout(self); row.setSpacing(6); row.setContentsMargins(0,0,0,0)
        for i in range(1, 11):
            b = QPushButton("•")
            b.setCheckable(True)
            b.setFixedWidth(24)
            b.clicked.connect(lambda _, n=i: self.set_value(n))
            self.dots.append(b); row.addWidget(b)
        self.update_ui()

    def set_value(self, n: int):
        self.value = n
        self.update_ui()

    def update_ui(self):
        for i, b in enumerate(self.dots, start=1):
            b.setChecked(i <= self.value)
            b.setStyleSheet("QPushButton {font-size:50px; border:none;} QPushButton:checked{color:black;} QPushButton{color:gray;}")

    def get_value(self) -> int:
        return self.value

    def clear(self):
        self.value = 0; self.update_ui()

class ChipsMultiSelect(QListWidget):
    """Simple multi-select list with nice UX."""
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setVisible(True)
        self.setMinimumHeight(self.sizeHintForRow(0) * 4 + 2 * self.frameWidth())

    def set_items(self, items):
        self.clear()
        for text, id_ in items:
            it = QListWidgetItem(text)
            it.setData(Qt.ItemDataRole.UserRole, id_)
            self.addItem(it)

    def selected_ids(self):
        return [i.data(Qt.ItemDataRole.UserRole) for i in self.selectedItems()]

    def select_ids(self, ids):
        for idx in range(self.count()):
            it = self.item(idx)
            if it.data(Qt.ItemDataRole.UserRole) in ids:
                it.setSelected(True)

class SuggestLine(QLineEdit):
    """Line edit with top-3 suggestions from DB table; commits new vibe rows when saving."""
    def __init__(self, table:str, column:str, pre_query=None, limit=3, capitalize=True):
        super().__init__()
        self.table, self.column, self.limit, self.capitalize = table, column, limit, capitalize
        self.pre_query = pre_query  # optional SQL to join/filter
        self.model = QStringListModel([])
        self.completer = QCompleter(self.model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(self.completer)
        self.textChanged.connect(self.requery)

    def requery(self, text):
        text = text.strip()
        rows = []
        if text:
            like = f"%{text}%"
            if self.pre_query:
                rows = fetchall(self.pre_query, (like,))
            else:
                rows = fetchall(f"SELECT {self.column} FROM {self.table} WHERE {self.column} LIKE ? ORDER BY {self.column} LIMIT {self.limit}", (like,))
        self.model.setStringList([r[0] for r in rows])

    def normalized_text(self):
        t = self.text().strip()
        return smart_title(t) if (t and self.capitalize) else t

class AddBookPage(QWidget):
    def __init__(self):
        super().__init__()

        # ----- top Save button and status -----
        self.status = QStatusBar()
        top_bar = QHBoxLayout()
        self.btnSaveTop = QPushButton("Save")
        self.btnSaveTop.clicked.connect(self.save_book)
        top_bar.addStretch(1)
        top_bar.addWidget(self.btnSaveTop)

        # ----- form in a scroll area -----
        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        # Icon (from DB)
        self.iconCombo = QComboBox()
        self.refresh_icons()
        self.form.addRow("Icon", self.iconCombo)

        # DNF
        self.chkDNF = QCheckBox("Did not finish")
        self.form.addRow("DNF", self.chkDNF)

        # Name (required, title-case)
        self.edName = QLineEdit()
        self.edName.editingFinished.connect(lambda: self.edName.setText(smart_title(self.edName.text())))
        self.form.addRow("Name *", self.edName)

        # Author (suggest top-3)
        self.edAuthor = SuggestLine(
            table="author",
            column="author_name",
            pre_query="SELECT author_name FROM author WHERE author_name LIKE ? ORDER BY author_name LIMIT 3",
            capitalize=True
        )
        self.edAuthor.editingFinished.connect(lambda: self.edAuthor.setText(self.edAuthor.normalized_text()))
        self.form.addRow("Author", self.edAuthor)

        # Size
        self.cbSize = QComboBox()
        for sid, name in fetchall("SELECT id, size_name FROM size ORDER BY id"):
            self.cbSize.addItem(name, sid)
        # default Novel
        idx = self.cbSize.findText("Novel — 200-450 pages")
        if idx >= 0: self.cbSize.setCurrentIndex(idx)
        self.form.addRow("Size", self.cbSize)

        # Category (radio)
        cat_options = fetchall("SELECT id, category_name FROM category ORDER BY id")
        self.wCategory, self.grpCategory = build_radio_group(cat_options)
        # default: Fiction checked
        for b in self.grpCategory.buttons():
            if b.text() == "Fiction":
                b.setChecked(True)
        # react when user switches
        for b in self.grpCategory.buttons():
            b.toggled.connect(self.on_category_change)

        self.form.addRow("Category", self.wCategory)


        # Genre (multi)
        self.lstGenre = ChipsMultiSelect()
        self.form.addRow("Genre (multi)", self.lstGenre)

        # Subgenre (multi, only for Fiction)
        self.subgenreContainer = QWidget()
        sgLayout = QVBoxLayout(self.subgenreContainer); sgLayout.setContentsMargins(0,0,0,0)
        self.lstSubgenre = ChipsMultiSelect()
        sgLayout.addWidget(self.lstSubgenre)
        self.form.addRow("Subgenre (multi)", self.subgenreContainer)

        # Source (multi)
        self.lstSource = ChipsMultiSelect()
        self.lstSource.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        sources = fetchall("SELECT id, source FROM source ORDER BY id")
        self.lstSource.set_items([(s[1], s[0]) for s in sources])
        self.form.addRow("Source (multi)", self.lstSource)

        # Discovery (multi) + text
        self.lstDiscovery = ChipsMultiSelect()
        discoveries = fetchall("SELECT id, discovery_name FROM discovery ORDER BY id")
        self.lstDiscovery.set_items([(d[1], d[0]) for d in discoveries])
        self.edDiscoveryText = QLineEdit()
        dwrap = QVBoxLayout(); dwrap.setContentsMargins(0,0,0,0)
        dbox = QWidget(); dbox.setLayout(dwrap)
        dwrap.addWidget(self.lstDiscovery)
        dwrap.addWidget(QLabel("Extra text"))
        dwrap.addWidget(self.edDiscoveryText)
        self.form.addRow("Where did I hear about it? (multi)", dbox)

        # Expectations fields
        self.txtExpect = QTextEdit()
        self.txtDiff = QTextEdit()
        self.form.addRow("My expectations", self.txtExpect)
        self.form.addRow("How different", self.txtDiff)

        # Dates
        self.dtStart = NullableDateEdit()
        self.dtFinish = NullableDateEdit()
        # if you want default NULL, do nothing; if you want default "today", call setDate(QDate.currentDate())
        self.form.addRow("Date started", self.dtStart)
        self.form.addRow("Date finished", self.dtFinish)


        # Rating (10 dots)
        self.dots = DotRating()
        self.form.addRow("Rating (1–10)", self.dots)

        # Vibe (user-extendable, top-3 suggestions)
        self.edVibes = MultiSuggestLine(table="vibe", column="vibe_name", limit=3, capitalize=True)
        self.form.addRow("Vibes (comma-separated)", self.edVibes)
        self.edVibes.setPlaceholderText("Type vibes, press Enter or comma (e.g. Satirical, Light, Rafe-style)")

        # Character crush list
        self.txtCrush = QLineEdit()
        self.form.addRow("Character crush list", self.txtCrush)

        # Months later (Hell yes / Vaguely / Who???)
        ml_options = fetchall("SELECT id, name FROM months_later")
        self.wMonthsLater, self.grpMonthsLater = build_radio_group(ml_options)
        # preselect first
        if self.grpMonthsLater.buttons(): self.grpMonthsLater.buttons()[0].setChecked(True)
        self.form.addRow("Do I remember it later?", self.wMonthsLater)

        # Reread (Absolutely / Maybe in crisis / Nah)
        rr_options = fetchall("SELECT id, name FROM reread")
        self.wReread, self.grpReread = build_radio_group(rr_options)
        if self.grpReread.buttons(): self.grpReread.buttons()[0].setChecked(True)
        self.form.addRow("Would I reread it?", self.wReread)

        # Line, Reminded, Phys copy, Notes
        self.edLine = QLineEdit()
        self.edReminded = QLineEdit()
        self.txtNotes = QTextEdit()
        self.form.addRow("That line that got me", self.edLine)
        self.form.addRow("What it reminded me of", self.edReminded)
        self.form.addRow("Notes", self.txtNotes)
        
        phys_opts = [(0,"No"), (1,"Yes")]
        self.wPhys, self.grpPhys = build_radio_group(phys_opts)
        # default No
        if self.grpPhys.buttons(): self.grpPhys.buttons()[0].setChecked(True)
        self.form.addRow("Need a physical copy?", self.wPhys)

        # Bottom Save button
        self.btnSaveBottom = QPushButton("Save")
        self.btnSaveBottom.clicked.connect(self.save_book)
        bottom_bar = QHBoxLayout(); bottom_bar.addStretch(1); bottom_bar.addWidget(self.btnSaveBottom)

        # assemble scroll area
        inner = QWidget(); innerForm = QVBoxLayout(inner)
        innerForm.addLayout(self.form)
        innerForm.addLayout(bottom_bar)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setWidget(inner)

        layout = QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.scroll)
        layout.addWidget(self.status)

        # load initial genre list for default category
        self.on_category_change()

    def refresh_icons(self):
        self.iconCombo.clear()
        self.iconCombo.addItem("(none)", None)
        icons = fetchall("SELECT id, name, path FROM icon ORDER BY name")
        for iid, name, path in icons:
            self.iconCombo.addItem(name, iid)

    def on_category_change(self):
        # find which radio is checked
        b = self.grpCategory.checkedButton()
        if not b:
            return
        cat_id = b.property("opt_id")
        cat_name = b.text()
        # reload genres for chosen category
        genres = fetchall("SELECT id, genre_name FROM genre WHERE category_id=? ORDER BY genre_name", (cat_id,))
        self.lstGenre.set_items([(g[1], g[0]) for g in genres])
        # subgenre visibility only for Fiction
        self.subgenreContainer.setVisible(cat_name == "Fiction")
        self.lstSubgenre.clear()
        # hook genre selection -> subgenres
        self.lstGenre.itemSelectionChanged.connect(self.load_subgenres)

    def load_subgenres(self):
        ids = self.lstGenre.selected_ids()
        if not ids:
            self.lstSubgenre.clear(); return
        placeholders = ",".join("?" for _ in ids)
        rows = fetchall(f"SELECT id, subgenre_name FROM subgenre WHERE genre_id IN ({placeholders}) ORDER BY subgenre_name", ids)
        self.lstSubgenre.set_items([(r[1], r[0]) for r in rows])

    def toast(self, text, ms=2000):
        self.status.showMessage(text, ms)

    def highlight(self, widget: QWidget, on=True):
        widget.setStyleSheet("border:1px solid #cc0000; border-radius:3px;" if on else "")

    def save_book(self):
        # reset highlights
        for w in [self.edName, self.dtStart, self.dtFinish]:
            self.highlight(w, False)

        # validations
        name = smart_title(self.edName.text())
        if not name:
            self.toast('Enter the Name', 10000)
            self.highlight(self.edName, True)
            self.scroll.ensureWidgetVisible(self.edName)
            return

        start = self.dtStart.get_or_none()
        finish = self.dtFinish.get_or_none()
        if start and finish and finish < start:
            self.toast("Date started can't be later than Date finished", 10000)
            self.highlight(self.dtStart, True)
            self.scroll.ensureWidgetVisible(self.dtStart)
            return

        # author: find or create if non-empty
        author_txt = self.edAuthor.normalized_text()
        author_id = None
        if author_txt:
            row = fetchone("SELECT id FROM author WHERE author_name=?", (author_txt,))
            if not row:
                exec_sql("INSERT INTO author(author_name) VALUES (?)", (author_txt,))
                row = fetchone("SELECT id FROM author WHERE author_name=?", (author_txt,))
            author_id = row[0]

        size_id = self.cbSize.currentData()
        cat_id = get_selected_radio_id(self.grpCategory)
        genre_ids = self.lstGenre.selected_ids()
        subgenre_ids = self.lstSubgenre.selected_ids() if self.subgenreContainer.isVisible() else []

        # source (multi): store main in books.source; extras ignored for now OR choose first
        source_ids = self.lstSource.selected_ids()
        source_id = source_ids[0] if source_ids else None  # you asked multi-select; books has single FK — we take first

        discovery_ids = self.lstDiscovery.selected_ids()
        discovery_id = discovery_ids[0] if discovery_ids else None  # same logic; first selected
        discovery_text = self.edDiscoveryText.text().strip() or None

        icon_id = self.iconCombo.currentData()
        dnf = 1 if self.chkDNF.isChecked() else 0
        rating10 = self.dots.get_value()
        crush = self.txtCrush.text().strip() or None
        line = self.edLine.text().strip() or None
        reminded = self.edReminded.text().strip() or None
        notes = self.txtNotes.toPlainText().strip() or None
        months_later_id = get_selected_radio_id(self.grpMonthsLater)
        reread_id       = get_selected_radio_id(self.grpReread)
        phys            = get_selected_radio_id(self.grpPhys) or 0

        # choose one genre/subgenre to save into books (because schema has single FKs)
        genre_id = genre_ids[0] if genre_ids else None
        subgenre_id = subgenre_ids[0] if subgenre_ids else None

        # insert
        try:
            conn = sqlite3.connect(DB_PATH, timeout=5)
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            # ensure author exists (if any)
            if author_txt:
                cur.execute("SELECT id FROM author WHERE author_name=?", (author_txt,))
                row = cur.fetchone()
                if not row:
                    cur.execute("INSERT INTO author(author_name) VALUES (?)", (author_txt,))
                    author_id = cur.lastrowid
                else:
                    author_id = row[0]

            # choose one genre/subgenre to save into books
            genre_id = genre_ids[0] if genre_ids else None
            subgenre_id = subgenre_ids[0] if subgenre_ids else None

            # insert book
            cur.execute("""
                INSERT INTO books
                (dnf, name, author, size, category, genre, subgenre, source, discovery, discovery_text,
                 icon, expectations, expectations_failed, date_start, date_finish, rating, crush_list,
                 months_later, reread, line, reminded, phys_copy, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dnf, name, author_id, size_id, cat_id, genre_id, subgenre_id,
                source_id, discovery_id, discovery_text,
                icon_id, self.txtExpect.toPlainText().strip() or None,
                self.txtDiff.toPlainText().strip() or None,
                start or None, finish or None, rating10, crush,
                months_later_id, reread_id, line, reminded, phys, notes
            ))

            book_id = cur.lastrowid

            # vibes
            for vibe_text in self.edVibes.get_tokens():
                cur.execute("SELECT id FROM vibe WHERE lower(vibe_name)=lower(?)", (vibe_text,))
                row = cur.fetchone()
                if not row:
                    cur.execute("INSERT INTO vibe(vibe_name, prefilled) VALUES (?, 0)", (vibe_text,))
                    vibe_id = cur.lastrowid
                else:
                    vibe_id = row[0]
                cur.execute("INSERT OR IGNORE INTO book_vibes(book_id, vibe_id) VALUES (?, ?)", (book_id, vibe_id))

            conn.commit()

        except Exception as e:
            if 'conn' in locals(): conn.rollback()
            self.toast(f"Save failed: {e}", 10000)
            return
        finally:
            if 'conn' in locals(): conn.close()


        # success feedback
        self.toast("Book saved", 5000)
        # clear form & scroll top
        self.reset_form()

    def reset_form(self):
        self.chkDNF.setChecked(False)
        self.edName.clear()
        self.edAuthor.clear()
        # keep defaults for size/category
        self.lstGenre.clearSelection()
        self.lstSubgenre.clear()
        for w in (self.lstSource, self.lstDiscovery):
            for i in range(w.count()): w.item(i).setSelected(False)
        self.edDiscoveryText.clear()
        self.txtExpect.clear()
        self.txtDiff.clear()
        self.dtStart.setDate(QDate.currentDate())
        self.dtFinish.setDate(QDate.currentDate())
        self.dots.clear()
        self.txtCrush.clear()
# re-check first radio in each group
        if self.grpMonthsLater.buttons(): self.grpMonthsLater.buttons()[0].setChecked(True)
        if self.grpReread.buttons():      self.grpReread.buttons()[0].setChecked(True)
        if self.grpPhys.buttons():        self.grpPhys.buttons()[0].setChecked(True)
        for b in self.grpCategory.buttons(): b.setChecked(b.text() == "Fiction")
        self.edLine.clear()
        self.edReminded.clear()
        self.txtNotes.clear()
        self.scroll.verticalScrollBar().setValue(0)
        # set first radio checked again (simple reset)
        if self.grpMonthsLater.buttons(): self.grpMonthsLater.buttons()[0].setChecked(True)
        if self.grpReread.buttons(): self.grpReread.buttons()[0].setChecked(True)
        if self.grpPhys.buttons(): self.grpPhys.buttons()[0].setChecked(True)
        self.edVibes.clear()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reading Journal — Add a book")
        self.resize(900, 800)

        # Top nav placeholders
        nav = QHBoxLayout()
        for label in ["My books","Add a book","Statistics","Settings"]:
            b = QPushButton(label)
            if label != "Add a book":
                b.clicked.connect(lambda _, t=label: QMessageBox.information(self, t, f"{t} — coming soon"))
            nav.addWidget(b)
        nav.addStretch(1)

        self.page = AddBookPage()

        root = QVBoxLayout(self)
        root.addLayout(nav)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); root.addWidget(sep)
        root.addWidget(self.page)

def main():
    if not os.path.exists(DB_PATH):
        QMessageBox.critical(None, "Error", f"Cannot find {DB_PATH}. Run db_setup.py first.")
        return
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    import sys
    # pick the one your code uses:
    from PyQt6.QtWidgets import QApplication  # if you're on PyQt6
    # from PySide6.QtWidgets import QApplication  # if you use PySide6

    app = QApplication(sys.argv)

    # make your main window only AFTER QApplication exists
    win = MainWindow()        # or whatever your top-level widget class is called
    win.show()

    sys.exit(app.exec())

