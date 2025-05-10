import streamlit as st
import random
import uuid

# --- Session State Initialization ---
if 'item_list' not in st.session_state:
    initial_tasks = [
        "Arreglar el aire acondicionado",
        "Poner la cerradura con código",
        "Poner la caja de llaves",
        "Comprar mesita para computadora",
        "Comprar un silla para la computadora", # Period removed for consistency
        "Comprar un cable de extensión multienchufe",
        "Comprar un horno multifuncional",
        "Comprar café normal",
        "Comprar café descafeinado",
        "Comprar te",
        "Comprar una máquina para hacer café, no greca",
        "Comprar jabón líquido para bañarse",
        "Comprar jabón líquido para lavar trastes",
        "Comprar jabón líquido para lavarse las manos",
        "6 conjuntos de sabana blancas",
        "Comprar una cámaratimbre de la marca Ring de batería",
        "Comprar dos baterías extra para la cámaratimbre",
        "Comprar cargador para las baterías", # Corrected typo
        "Comprar la bocina para la cámara timbre", # Corrected typo
        "Comprar un secador de pelo básico",
        "Comprar un Extintor 🧯",
        "Comprar un Detector de humo y monóxido de carbono",
        "Comprar un Botiquín de primeros auxilios",
        "Comprar una canasta 🧺 para hacerle el regalo de bienvenida",
        "Comprar Juegos de mesa ♟️ como monopolio y cartas",
        "Comprar toallas",
        "Comprar cartón que va encima de los armarios",
        "Comprar percha para las ropas"
    ]
    st.session_state.item_list = [
        {"id": str(uuid.uuid4()), "text": task_text, "completed": False} for task_text in initial_tasks
    ]
if 'hop_item_id' not in st.session_state:
    st.session_state.hop_item_id = st.session_state.item_list[0]['id'] if st.session_state.item_list else None

st.title("Lista de Pendientes Estilo iPhone")

st.write(
    "Gestiona tus tareas al estilo de los Recordatorios de iPhone. "
    "Haz clic en '¡Saltar!' para destacar una tarea activa al azar."
)

# --- Display Reminders ---
for item in st.session_state.item_list:
    item_id = item['id']
    is_completed = item['completed']
    display_text = item['text']

    if item_id == st.session_state.hop_item_id and not is_completed:
        display_text = f"➡️ {display_text}"
    
    # Use a unique key for each checkbox based on item_id
    
    def on_checkbox_change(changed_item_id):
        # Find the item and update its completed status
        for task_item in st.session_state.item_list:
            if task_item['id'] == changed_item_id:
                # The new value of the checkbox is already in st.session_state under its key
                task_item['completed'] = st.session_state[f"cb_{changed_item_id}"]
                
                # If a hopped item is completed, adjust hop_item_id
                if changed_item_id == st.session_state.hop_item_id and task_item['completed']:
                    active_items_ids = [i['id'] for i in st.session_state.item_list if not i['completed']]
                    if active_items_ids:
                        # Try to pick a different active item if possible
                        possible_next_hops = [id_ for id_ in active_items_ids if id_ != st.session_state.hop_item_id]
                        if possible_next_hops:
                             st.session_state.hop_item_id = random.choice(possible_next_hops)
                        else: # Only one active item left (the one just completed was the only other, or it was the only one)
                             st.session_state.hop_item_id = random.choice(active_items_ids) if active_items_ids else None
                    else:
                        st.session_state.hop_item_id = None
                break
        # No explicit st.rerun() needed here, on_change handles it.

    st.checkbox(
        display_text,
        value=item['completed'], # Directly use item's current completed status
        key=f"cb_{item_id}",
        on_change=on_checkbox_change,
        args=(item_id,) 
    )

# --- Hop Button ---
if st.button("¡Saltar!"):
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
st.sidebar.header("Controles")
new_item_text = st.sidebar.text_input("Añadir nuevo recordatorio:", key="new_item_text_input")

if st.sidebar.button("Añadir Recordatorio"):
    if new_item_text:
        new_id = str(uuid.uuid4())
        st.session_state.item_list.insert(0, {"id": new_id, "text": new_item_text, "completed": False}) # Insert at the beginning
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
        "Eliminar un recordatorio:",
        options=options_for_removal,
        format_func=lambda x: x[0], # Display the text part of the tuple
        index=None,
        placeholder="Selecciona recordatorio para eliminar",
        key="remove_selectbox"
    )

    if st.sidebar.button("Eliminar Recordatorio Seleccionado"):
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
