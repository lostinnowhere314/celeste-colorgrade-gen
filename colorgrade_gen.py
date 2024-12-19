import numpy as np
from collections import namedtuple
from functools import wraps
from colorgrade_core import *
from colorgrade_steps import *
    
## Page functionality

new_process_id = 0
process_steps = []
no_input_process_types = {'if-else', 'fill'}

# get needed globals from the javascript
import js
from js import canvas, canvas_ctx, process_items, document, error_message, clear_err_message
from pyscript import when
from pyscript.ffi import create_proxy

#from pyscript.ffi import create_proxy
#document.proxy_generate = create_proxy(generate)

@when("click", "#generate")
def handler_generate(event):
    clear_err_message()
    generate()

@when("click", "#simplerecolor")
def handler_simple_recolor(event):
    clear_err_message()
    create_process_step('simple-recolor')
@when("click", "#eightvaluerecolor")
def handler_8_value_recolor(event):
    clear_err_message()
    create_process_step('8-value-recolor')
@when("click", "#recentercolors")
def handler_recenter_colors(event):
    clear_err_message()
    create_process_step('recenter-colors')
@when("click", "#fill")
def handler_fill(event):
    clear_err_message()
    create_process_step('fill')
@when("click", "#ifelse")
def handler_if_else(event):
    clear_err_message()
    create_process_step('if-else')
@when("click", "#adjustrgb")
def handler_adjust_rgb(event):
    clear_err_message()
    create_process_step('adjust-rgb')
@when("click", "#adjusthsv")
def handler_adjust_hsv(event):
    clear_err_message()
    create_process_step('adjust-hsv')
@when("click", "#brightnesscontrast")
def handler_brightness_contrast(event):
    clear_err_message()
    create_process_step('brightness-contrast')
@when("click", "#custom")
def handler_custom(event):
    clear_err_message()
    create_process_step('custom')
@when("click", "#reducecolors")
def handler_reducecolors(event):
    clear_err_message()
    create_process_step('reduce-colors')
@when("click", "#palettize")
def handler_palettize(event):
    clear_err_message()
    create_process_step('palettize')

def setup_page():
	write_colorgrade(get_default_colorgrade())
	create_process_step('8-value-recolor')
	hide_loading_overlay()


def hide_loading_overlay():
    js.JsLoadingOverlay.hide()

# Wrapper for displaying errors to our html element
def display_errors(fn):
    @wraps(fn)
    def _inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            # Display the error
            show_error_exception(
                e, 
                prefix=f"Error in {fn.__name__}():", 
                post="See developer console for full stack trace."
            )
            # Raise anyways so that the whole stacktrace makes it to the log
            raise
    return _inner

@display_errors
def create_process_step(process_type):
    """
    Creates a process item
    """
    global new_process_id
    
    ## Create the new element
    element = create_element_with_tags(
        "div",
        process_id=str(new_process_id),
        _class="step_box",
    )
    # alternative to this bit: use eval
    process_step = {
        '8-value-recolor': CG8ValueRecolor,
        'simple-recolor': CGSimpleRecolor,
        'recenter-colors': CGRecenterColors,
        'fill': CGFill,
        'if-else': CGIfElse,
        'adjust-rgb': CGAdjustRGB,
        'adjust-hsv': CGAdjustHSV,
        'brightness-contrast': CGBrightnessContrast,
        'palettize': CGPalettize,
        'reduce-colors': CGReduceColors,
        'custom': CGCustomMap,
    }[process_type](new_process_id, element, process_type)
    
    ## Populate the element
    # Index and display name 
    element.appendChild(create_element_with_tags(
        "strong", text=str(len(process_steps)+1), id='process_index',
    ))
    element.appendChild(create_element_with_tags(
        "strong", text=f'. {process_step.title()}' 
    ))
    element.appendChild(create_element_with_tags(
        "br", 
    ))
    
    # Populate with method-specific tags
    process_step.populate_html_element(element)
    
    ## Row for the source colorgrade and the buttons
    last_line_supercontainer = create_element_with_tags('table', _class='step_box_button_container')
    last_line_subcontainer = create_element_with_tags('tr')
    
    if process_step.has_input():
        # Add a box for which step to take as input colorgrade
        source_holder = create_element_with_tags('td', align='left')
        add_input_field(source_holder, 'which-step', 'Source step: ', '-1', size=2)
        last_line_subcontainer.appendChild(source_holder)
        
    end_buttons = create_element_with_tags('td', align='right')
    # Add buttons for moving up and down
    end_buttons.appendChild(create_element_with_tags(
        'button',
        onclick=f'move_up({new_process_id})',
        text='^',
    ))
    end_buttons.appendChild(create_element_with_tags(
        'button',
        onclick=f'move_down({new_process_id})',
        text='v',
    ))
    # Add the 'X' button at the end
    end_buttons.appendChild(create_element_with_tags(
        'button',
        onclick=f'remove_process_step({new_process_id})',
        id=f'button-remove-{new_process_id}',
        text='X',
    ))
    last_line_subcontainer.appendChild(end_buttons)
    #finish attaching
    last_line_supercontainer.appendChild(last_line_subcontainer)
    element.appendChild(last_line_supercontainer)
    
    ## Insert the element
    process_items.appendChild(element)
    ## Add to our list
    process_steps.append(process_step)
    
    # Update what the next process's ID will be
    new_process_id += 1

def get_index_of_step(process_id):
    """
    Gets the index of the process step with given integer id
    """
    process_id = int(process_id)
    
    for i, step in enumerate(process_steps):
        if step.process_id == process_id:
            return i
    
    return None

@display_errors
def remove_process_step(process_id):
    """
    Attempts to remove the process with the given integer id.
    """
    process_id = int(process_id)
    
    process_index = get_index_of_step(process_id)
    if process_index is None:
        raise ValueError(f"unable to find process with id {process_id}")
        
    # Remove from list
    to_remove = process_steps.pop(process_index)
    # Remove HTML element
    to_remove.element.remove()
    
    regenerate_display_indices()
        
def regenerate_display_indices():
    """
    Iterates through each process step and re-sets its display index
    """
    for i, step in enumerate(process_steps, start=1):
        step.element.querySelector("#process_index").innerHTML = str(i)
    
@display_errors
def move_step_up(process_id):
    """
    Moves the given step up one (unless it's at the beginning)
    """
    process_id = int(process_id)
    
    process_index = get_index_of_step(process_id)
    if process_index is None:
        raise ValueError(f"unable to find process with id {process_id}")
    if process_index == 0:
        return
        
    # Move within list
    step = process_steps.pop(process_index)
    process_steps.insert(process_index - 1, step)
    # Move HTML element
    process_items.insertBefore(step.element, step.element.previousElementSibling);
    
    regenerate_display_indices()
    clear_err_message()
    
@display_errors
def move_step_down(process_id):
    """
    Moves the given step down one (unless it's at the end)
    """
    process_id = int(process_id)
    
    process_index = get_index_of_step(process_id)
    if process_index is None:
        raise ValueError(f"unable to find process with id {process_id}")
    if process_index == len(process_steps) - 1:
        return
        
    # Move within list
    step = process_steps.pop(process_index)
    process_steps.insert(process_index + 1, step)
    # Move HTML element
    process_items.insertBefore(step.element, step.element.nextElementSibling.nextElementSibling);
    
    regenerate_display_indices()
    hide_error()
    
def generate():
    """
    Generates the colorgrade using the given values
    note to self: in the future, add something to handle exceptions that occur
    """
    hide_error()
    cg_steps = [get_default_colorgrade()]
    
    for i, process_step in enumerate(process_steps, start=1):
        cg_out = None
        try:
            cg_steps.append(
                process_step.do_processing(cg_steps)
            )
            
        except Exception as e:
            show_error_exception(
                e,
                prefix=f"Error parsing step {i}:",
                show_error_type=False,
            )
            raise
        
    result = cg_steps[-1]
    write_colorgrade(result)

def write_colorgrade(cg):
    """
    Writes the colorgrade to the canvas object
    """
    flat_cg = process_colorgrade(cg)
    for i in range(256):
        for j in range(16):
            canvas_ctx.fillStyle = f"rgb({flat_cg[i,j,0]},{flat_cg[i,j,1]},{flat_cg[i,j,2]})"
            canvas_ctx.fillRect(i, j, 1, 1)
    
def show_error_exception(e, prefix="Error:", post="", show_error_type=True):
    """
    Displays the exception in the error box
    """
    if len(prefix) > 0:
        prefix = prefix+' '
    if len(post) > 0:
        post = ' ' + post
    if show_error_type:
        class_name = f"{e.__class__.__name__}: "
    else:
        class_name = ""
    message = f"{prefix}{class_name}{str(e)}.{post}"
    show_error_text(message)
    
def show_error_text(error_text):
    """
    Displays the given text to the error box
    """
    error_message.innerHTML = error_text
    error_message.style.display = 'block'
    
def hide_error():
    """
    Displays the given text to the error box
    """
    error_message.style.display = 'hide'
    
# Proxy functions
js.move_step_up = create_proxy(move_step_up)
js.move_step_down = create_proxy(move_step_down)
js.remove_process_step_proxy = create_proxy(remove_process_step)
