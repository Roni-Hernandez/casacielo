import streamlit as st
import random
import uuid

# --- Session State Initialization ---
if 'item_list' not in st.session_state:
    st.session_state.item_list = [
        {"id": str(uuid.uuid4()), "text": f"Item {i+1}", "completed": False} for i in range(3)
    ]
if 'hop_item_id' not in st.session_state:
    st.session_state.hop_item_id = st.session_state.item_list[0]['id'] if st.session_state.item_list else None

st.title("iPhone Style Reminders")

st.write(
    "Manage your tasks like iPhone Reminders. "
    "Click 'Hop!' to highlight a random active task."
)

# --- Display Reminders ---
for item in st.session_state.item_list:
    item_id = item['id']
    is_completed = item['completed']
    display_text = item['text']

    if item_id == st.session_state.hop_item_id and not is_completed:
        display_text = f"➡️ {display_text}"
    
    # Use a unique key for each checkbox based on item_id
    new_completed_status = st.checkbox(
        display_text, 
        value=is_completed, 
        key=f"cb_{item_id}"
    )
    if new_completed_status != is_completed:
        item['completed'] = new_completed_status
        # If a hopped item is completed, remove hop or pick a new one
        if item_id == st.session_state.hop_item_id and new_completed_status:
            active_items = [i['id'] for i in st.session_state.item_list if not i['completed']]
            if active_items:
                st.session_state.hop_item_id = random.choice(active_items)
            else:
                st.session_state.hop_item_id = None
        st.rerun()

# --- Hop Button ---
if st.button("Hop!"):
    active_items_ids = [item['id'] for item in st.session_state.item_list if not item['completed']]
    if active_items_ids:
        current_hop_id = st.session_state.hop_item_id
        possible_next_hops = [id_ for id_ in active_items_ids if id_ != current_hop_id]
        
        if possible_next_hops:
            st.session_state.hop_item_id = random.choice(possible_next_hops)
        elif active_items_ids: # Only one active item, or current hop is the only active
            st.session_state.hop_item_id = active_items_ids[0]
        else: # No active items
            st.session_state.hop_item_id = None
    else:
        st.session_state.hop_item_id = None
    st.rerun()

# --- Sidebar Controls ---
st.sidebar.header("Controls")
new_item_text = st.sidebar.text_input("Add new reminder:", key="new_item_text_input")

if st.sidebar.button("Add Reminder"):
    if new_item_text:
        new_id = str(uuid.uuid4())
        st.session_state.item_list.append({"id": new_id, "text": new_item_text, "completed": False})
        if st.session_state.hop_item_id is None: # If no item was hopped, hop to the new one
            st.session_state.hop_item_id = new_id
        new_item_text = "" # Clear input, though Streamlit handles this with rerun
        st.rerun()

if st.session_state.item_list:
    # Create a list of tuples (display_text, item_id) for the selectbox
    # Show completed items with a (✓) prefix for clarity in removal list
    options_for_removal = []
    for item in st.session_state.item_list:
        prefix = "(✓) " if item['completed'] else "( ) "
        options_for_removal.append((f"{prefix}{item['text']}", item['id']))

    # The selectbox will show the first element of the tuple, but return the second (item_id)
    selected_tuple_for_removal = st.sidebar.selectbox(
        "Remove a reminder:",
        options=options_for_removal,
        format_func=lambda x: x[0], # Display the text part of the tuple
        index=None,
        placeholder="Select reminder to remove",
        key="remove_selectbox"
    )

    if st.sidebar.button("Remove Selected Reminder"):
        if selected_tuple_for_removal:
            item_id_to_remove = selected_tuple_for_removal[1] # Get the id
            st.session_state.item_list = [item for item in st.session_state.item_list if item['id'] != item_id_to_remove]
            
            # If the removed item was the hopped one, pick a new one
            if st.session_state.hop_item_id == item_id_to_remove:
                active_items = [i['id'] for i in st.session_state.item_list if not i['completed']]
                if active_items:
                    st.session_state.hop_item_id = random.choice(active_items)
                else:
                    st.session_state.hop_item_id = None
            st.rerun()

st.markdown("---")
# For debugging or clarity, show the raw list structure
# st.write("Debug: Current item list:", st.session_state.item_list)
# st.write("Debug: Hop item ID:", st.session_state.hop_item_id)
