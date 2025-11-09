import json
import os
import uuid
from datetime import datetime

import streamlit as st

DATA_FILE = "todos.json"

# ---------- Data layer ----------
def load_todos():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If the file is corrupted, start fresh
        return []

def save_todos(todos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)

# ---------- Small helper ----------
def rerun():
    # Streamlit changed API names over time; this keeps us safe
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# ---------- App setup ----------
st.set_page_config(page_title="To-Do", page_icon="✅", layout="centered")
st.title("✅ To-Do List")

# Load once into session_state
if "todos" not in st.session_state:
    st.session_state.todos = load_todos()

# ---------- Sidebar: filters & file ops ----------
with st.sidebar:
    st.header("Options")
    filter_choice = st.radio("Show", ["All", "Active", "Completed"], horizontal=True)
    search = st.text_input("Search", placeholder="Filter tasks by text...")
    if st.button("💾 Save to disk"):
        save_todos(st.session_state.todos)
        st.success("Saved todos.json")
    if st.button("🔄 Reload from disk"):
        st.session_state.todos = load_todos()
        st.info("Reloaded from todos.json")
        rerun()
    st.caption(f"Data file: {os.path.abspath(DATA_FILE)}")

# ---------- Add new task ----------
with st.form("add_form", clear_on_submit=True):
    new_text = st.text_input("Add a new task", placeholder="e.g., Buy milk")
    submitted = st.form_submit_button("Add")
    if submitted:
        if new_text.strip():
            st.session_state.todos.append({
                "id": str(uuid.uuid4()),
                "text": new_text.strip(),
                "done": False,
                "created_at": now_str()
            })
            save_todos(st.session_state.todos)
            st.toast("Added task")
            rerun()
        else:
            st.warning("Please type something.")

# ---------- Filtering ----------
def filtered_todos():
    todos = st.session_state.todos
    if search:
        q = search.lower()
        todos = [t for t in todos if q in t["text"].lower()]
    if filter_choice == "Active":
        todos = [t for t in todos if not t["done"]]
    elif filter_choice == "Completed":
        todos = [t for t in todos if t["done"]]
    return todos

todos_to_show = filtered_todos()
st.subheader(f"Tasks ({len(todos_to_show)}/{len(st.session_state.todos)})")

# ---------- List + inline edit/delete ----------
if not todos_to_show:
    st.info("No tasks to show. Add one above!")
else:
    for todo in todos_to_show:
        # index in the master list
        idx = next(i for i, t in enumerate(st.session_state.todos) if t["id"] == todo["id"])

        cols = st.columns([0.08, 0.67, 0.25])
        with cols[0]:
            checked = st.checkbox("", value=todo["done"], key=f"chk_{todo['id']}")
            if checked != st.session_state.todos[idx]["done"]:
                st.session_state.todos[idx]["done"] = checked
                save_todos(st.session_state.todos)
                rerun()

        with cols[1]:
            new_val = st.text_input(
                label="",
                value=todo["text"],
                key=f"txt_{todo['id']}",
                label_visibility="collapsed",
                placeholder="Edit task..."
            )

        with cols[2]:
            update = st.button("Update", key=f"upd_{todo['id']}")
            delete = st.button("Delete", key=f"del_{todo['id']}")
            if update:
                st.session_state.todos[idx]["text"] = new_val.strip()
                save_todos(st.session_state.todos)
                st.toast("Updated")
                rerun()
            if delete:
                st.session_state.todos.pop(idx)
                save_todos(st.session_state.todos)
                st.toast("Deleted")
                rerun()

# ---------- Bulk actions ----------
with st.expander("Bulk actions"):
    c1, c2, c3 = st.columns(3)
    if c1.button("Mark all completed"):
        for t in st.session_state.todos:
            t["done"] = True
        save_todos(st.session_state.todos)
        rerun()
    if c2.button("Mark all active"):
        for t in st.session_state.todos:
            t["done"] = False
        save_todos(st.session_state.todos)
        rerun()
    if c3.button("Delete completed"):
        st.session_state.todos = [t for t in st.session_state.todos if not t["done"]]
        save_todos(st.session_state.todos)
        rerun()

st.caption("Made with Streamlit • Data is saved in a local JSON file (todos.json)")
