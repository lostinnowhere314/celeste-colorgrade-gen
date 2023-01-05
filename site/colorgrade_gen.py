import numpy as np
from collections import namedtuple
from colorgrade_core import *
    
## Page functionality

new_process_id = 0
ProcessStep = namedtuple("ProcessStep", [
    "process_id",
    "process_type",
    "html_element",
])
process_steps = []

# get needed globals
from js import canvas, canvas_ctx, process_items, document


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
    
    # Populate the element
    
    if process_type == "8-value-recolor":
        element.appendChild(create_element_with_tags(
            "strong", text='8-value recolor' 
        ))
        element.appendChild(create_element_with_tags(
            "br", 
        ))
        
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
            "strong", text='Simple recolor' 
        ))
        element.appendChild(create_element_with_tags(
            "br", 
        ))
        
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
    else:
        raise ValueError(f"invalid process type '{process_type}'")
    
    # Add the 'X' button at the end
    end_buttons = create_element_with_tags('div', align='right')
    end_buttons.appendChild(create_element_with_tags(
        'button',
        onclick=f'remove_process_step({new_process_id})',
        id=f'button-remove-{new_process_id}',
        text='X',
    ))
    element.appendChild(end_buttons)
    
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

def remove_process_step(process_id):
    """
    Attempts to remove the process with the given integer id.
    """
    process_id = int(process_id)
    
    # Find the process with this ID in our list
    for i in range(len(process_steps)):
        if process_steps[i].process_id == process_id:
            to_remove = process_steps[i]
            # Remove from list
            process_steps.pop(i)
            # Remove HTML element
            to_remove.html_element.remove()
            
            return
    
    raise ValueError(f"unable to find process with id {process_id}")
    
    
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
    
def generate():
    """
    Generates the colorgrade using the given values
    note to self: in the future, add something to handle exceptions that occur
    """
    
    cg_steps = [get_default_colorgrade()]
    
    for process_step in process_steps:
        cg_in = cg_steps[-1] #in the future, generalize this
        
        if process_step.process_type == "8-value-recolor":
            colors = parse_arguments_from_element(process_step.html_element, ['black','white','red','green','blue','yellow','magenta','cyan'])
            colors_scalar = [parse_color(c) for c in colors]
            cg_out = linear_recolor(cg_in, colors_scalar)
            
        elif process_step.process_type == "simple-recolor":
            colors = parse_arguments_from_element(process_step.html_element, ['black','white'])
            colors_scalar = [parse_color(c) for c in colors]
            cg_out = simple_recolor(cg_in, *colors_scalar)
            
        else:
            raise NotImplemented()
        
        cg_steps.append(cg_out)
        
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
    
