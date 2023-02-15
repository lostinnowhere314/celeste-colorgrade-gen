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
from js import canvas, canvas_ctx, process_items, error_message


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
        'recenter-colors': None,
        'fill': None,
        'if-else': None,
        'adjust-rgb': None,
        'adjust-hsv': None,
        'brightness-contrast': None,
        'custom': None,
    }[process_type](new_process_id, element)
    
    
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
    
    if False: ## Old method; delete when done porting ##
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
            add_input_field(element, 'g-shift', ' G shift: ', "0.0", size=4)
            element.appendChild(create_element_with_tags("br"))
            add_input_field(element, 'b-shift', ' B shift: ', "0.0", size=4)
        elif process_type == "adjust-hsv":
            add_input_field(element, 'h-shift', ' H shift: ', "0.0", size=4)
            element.appendChild(create_element_with_tags("br"))
            add_input_field(element, 's-shift', ' S shift: ', "0.0", size=4)
            element.appendChild(create_element_with_tags("br"))
            add_input_field(element, 'v-shift', ' V shift: ', "0.0", size=4)
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
    ## End old version ##
    
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
    hide_error()
    
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
            
            if False: ## Old organization; delete when done refactoring ##
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
            ## End old version ##
            
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
    