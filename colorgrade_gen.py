import numpy as np
from collections import namedtuple
from functools import wraps
from colorgrade_core import *
    
## Page functionality

new_process_id = 0
ProcessStep = namedtuple("ProcessStep", [
    "process_id",
    "process_type",
    "html_element",
])
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
def create_element_with_tags(el_type, **tags):
    """
    Creates a HTML element with the given tags.
    An initial underscore is ignored.
    Otherwise, underscores are replaced with dashes
    """
    element = document.createElement(el_type)
    
    text = tags.pop('text', None)
    
    for tag in tags:
        if tag[0] == "_":
            element.setAttribute(tag[1:], tags[tag])
        else:
            element.setAttribute(tag.replace('_','-'), tags[tag])
            
    if text is not None:
        element.innerHTML = text
            
    return element

def add_input_field(parent, name, label, value, size=4, **kwargs):
    parent.appendChild(create_element_with_tags(
        "label", _for=name, text=label
    ))
    parent.appendChild(create_element_with_tags(
        "input", _type='text', name=name, id=name, value=value, size=size, **kwargs
    ))

@display_errors
def create_process_step(process_type):
    """
    Creates a process item
    """
    global new_process_id
    
    # Create the new element
    element = create_element_with_tags(
        "div",
        process_id=str(new_process_id),
        _class="step_box",
    )
    
    ## Populate the element
    # Index and display name 
    element.appendChild(create_element_with_tags(
        "strong", text=str(len(process_steps)+1), id='process_index',
    ))
    title = {
        "8-value-recolor": "8-value recolor",
        "simple-recolor": "Simple recolor",
        "fill": "Fill",
        "if-else": "Condition",
        "adjust-rgb": "Adjust RGB",
        "adjust-hsv": "Adjust HSV",
        "brightness-contrast": "Brightness/contrast",
        "recenter-colors": "Recenter colors",
        "custom": "Custom RGB map",
    }[process_type]
    element.appendChild(create_element_with_tags(
        "strong", text=f'. {title}' 
    ))
    element.appendChild(create_element_with_tags(
        "br", 
    ))
    
    if process_type == "8-value-recolor":
        element.appendChild(create_element_with_tags(
            "label", _for='black', text=' Black: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='black', id='black', value='000000', size=4
        ))
        element.appendChild(create_element_with_tags(
            "label", _for='white', text=' White: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='white', id='white', value='FFFFFF', size=4
        ))
        element.appendChild(create_element_with_tags(
            "br", 
        ))
        
        element.appendChild(create_element_with_tags(
            "label", _for='red', text=' Red: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='red', id='red', value='FF0000', size=4
        ))
        element.appendChild(create_element_with_tags(
            "label", _for='green', text=' Green: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='green', id='green', value='00FF00', size=4
        ))
        element.appendChild(create_element_with_tags(
            "br", 
        ))
        
        element.appendChild(create_element_with_tags(
            "label", _for='blue', text=' Blue: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='blue', id='blue', value='0000FF', size=4
        ))
        element.appendChild(create_element_with_tags(
            "label", _for='yellow', text=' Yellow: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='yellow', id='yellow', value='FFFF00', size=4
        ))
        element.appendChild(create_element_with_tags(
            "br", 
        ))
        
        element.appendChild(create_element_with_tags(
            "label", _for='magenta', text=' Magenta: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='magenta', id='magenta', value='FF00FF', size=4
        ))
        element.appendChild(create_element_with_tags(
            "label", _for='cyan', text=' Cyan: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='cyan', id='cyan', value='00FFFF', size=4
        ))
    elif process_type == "simple-recolor":
        
        element.appendChild(create_element_with_tags(
            "label", _for='black', text=' Black: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='black', id='black', value='000000', size=4
        ))
        element.appendChild(create_element_with_tags(
            "label", _for='white', text=' White: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='white', id='white', value='FFFFFF', size=4
        ))
    elif process_type == "recenter-colors":
        # Takes no parameters
        pass
    elif process_type == "fill":
        element.appendChild(create_element_with_tags(
            "label", _for='color', text='Color: '
        ))
        element.appendChild(create_element_with_tags(
            "input", _type='text', name='color', id='color', value='000000', size=4
        ))
    elif process_type == "if-else":
        add_input_field(element, 'condition', ' Condition: ', 'r+g+b > 0.5', size=24)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'cond-input', 'Condition source: ', '0', size=2)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'true-input', 'Source if true: ', '-1', size=2)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'false-input', 'Source if false: ', '-1', size=2)
        
    elif process_type == "adjust-rgb":
        add_input_field(element, 'r-shift', ' R shift: ', "0.0", size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'g-shift', ' B shift: ', "0.0", size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'b-shift', ' G shift: ', "0.0", size=4)
    elif process_type == "adjust-hsv":
        add_input_field(element, 'h-shift', ' H shift: ', "0.0", size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 's-shift', ' V shift: ', "0.0", size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'v-shift', ' S shift: ', "0.0", size=4)
    elif process_type == "brightness-contrast":
        add_input_field(element, 'bright-shift', ' Brightness: ', "0.0", size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'con-shift', ' Contrast: ', "0.0", size=4)
    elif process_type == "custom":
        add_input_field(element, 'new-r', ' New R: ', 'r', size=24)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'new-g', ' New G: ', 'g', size=24)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'new-b', ' New B: ', 'b', size=24)
    else:
        raise ValueError(f"invalid process type '{process_type}'")
    
    # Row for the source colorgrade and the buttons
    last_line_supercontainer = create_element_with_tags('table', _class='step_box_button_container')
    last_line_subcontainer = create_element_with_tags('tr')
    
    if process_type not in no_input_process_types:
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
    
    # Create the element
    process_items.appendChild(element)
    # Add to our list
    process_steps.append(ProcessStep(
        new_process_id,
        process_type,
        element,
    ))
    
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
    to_remove.html_element.remove()
    
    regenerate_display_indices()
        
def parse_arguments_from_element(element, ids):
    """
    Gets the arguments from the element from input items with the given ids, and returns them as a list
    """
    results = []
    
    for id in ids:
        child = element.querySelector(f"#{id}")
        
        if child is None:
            raise ValueError(f"could not find node with id {id}")
            
        results.append(child.value)
        
    return results
    
def regenerate_display_indices():
    """
    Iterates through each process step and re-sets its display index
    """
    for i, step in enumerate(process_steps, start=1):
        step.html_element.querySelector("#process_index").innerHTML = str(i)
    
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
    process_items.insertBefore(step.html_element, step.html_element.previousElementSibling);
    
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
    process_items.insertBefore(step.html_element, step.html_element.nextElementSibling.nextElementSibling);
    
    regenerate_display_indices()
    
def generate():
    """
    Generates the colorgrade using the given values
    note to self: in the future, add something to handle exceptions that occur
    """
    cg_steps = [get_default_colorgrade()]
    
    for i, process_step in enumerate(process_steps, start=1):
        cg_out = None
        try:
        
            # Find input
            if process_step.process_type not in no_input_process_types:
                target_index = int(parse_arguments_from_element(process_step.html_element, ['which-step'])[0])
                cg_in = cg_steps[target_index]
            else:   
                cg_in = None
            
            
            # Run the step
            if process_step.process_type == "8-value-recolor":
                colors = parse_arguments_from_element(process_step.html_element, ['black','white','red','green','blue','yellow','magenta','cyan'])
                colors_scalar = [parse_color(c) for c in colors]
                cg_out = linear_recolor(cg_in, colors_scalar)
                
            elif process_step.process_type == "simple-recolor":
                colors = parse_arguments_from_element(process_step.html_element, ['black','white'])
                colors_scalar = [parse_color(c) for c in colors]
                cg_out = simple_recolor(cg_in, *colors_scalar)
                
            elif process_step.process_type == "recenter-colors":
                cg_out = rescale_to_fill_range(cg_in)
                
            elif process_step.process_type == "fill":
                color = parse_color(
                    parse_arguments_from_element(
                        process_step.html_element,
                        ['color']
                    )[0]
                )
                cg_out = get_filled_colorgrade(color)
                
            elif process_step.process_type == "if-else":
                condition, cond_idx, true_idx, false_idx = parse_arguments_from_element(
                    process_step.html_element,
                    ['condition', 'cond-input', 'true-input', 'false-input']
                )
                cg_true = cg_steps[int(true_idx)]
                cg_false = cg_steps[int(false_idx)]
                cg_cond = cg_steps[int(cond_idx)]
                
                cg_out = if_else(cg_true, cg_false, cg_cond, condition)
                
            elif process_step.process_type == "adjust-rgb":
                shifts = [
                    float(val)
                    for val in parse_arguments_from_element(
                        process_step.html_element,
                        ['r-shift', 'g-shift', 'b-shift']
                    )
                ]
                
                cg_out = adjust_rgb(cg_in, *shifts)
                
            elif process_step.process_type == "adjust-hsv":
                shifts = [
                    float(val)
                    for val in parse_arguments_from_element(
                        process_step.html_element,
                        ['h-shift', 's-shift', 'v-shift']
                    )
                ]
                
                cg_out = adjust_hsv(cg_in, *shifts)
                
            elif process_step.process_type == "brightness-contrast":
                shifts = [
                    float(val)
                    for val in parse_arguments_from_element(
                        process_step.html_element,
                        ['bright-shift', 'con-shift']
                    )
                ]
                
                cg_out = brightness_contrast(cg_in, *shifts)
                
            elif process_step.process_type == "custom":
                expressions = parse_arguments_from_element(
                    process_step.html_element,
                    ['new-r', 'new-g', 'new-b']
                )
                
                cg_out = custom_rgb_adjust(cg_in, *expressions)
                
            else:
                raise NotImplementedError(f"unknown proess type '{process_step.process_type}'")
            if cg_out is None:
                raise RuntimeError(f"`cg_out` did not get set with process of type '{process_step.process_type}'")
                
            cg_steps.append(cg_out)
        
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
    
js.move_step_up = create_proxy(move_step_up)
js.move_step_down = create_proxy(move_step_down)
