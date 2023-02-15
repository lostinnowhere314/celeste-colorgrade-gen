"""
Defines classes for interfacing between the HTML and 
applying colorgrade effects.
"""

from colorgrade_core import *
from js import document

### Utility functions
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

### Abstract class

class ColorgradeProcessStep:
    """
    Template class for a colorgrade processing step.
    """
    def __init__(self, process_id, element):
        """
        Creates a new process step
        """
        self.process_id = process_id
        self.element = element
    
    def get_target_index(self):
        """
        Returns the index of the input target
        """
        return int(parse_arguments_from_element(self.element, ['which-step'])[0])
    
    # this is not a good way of doing it but I don't want to deal with the alternatives
    def title(self):
        """String title"""
        raise NotImplementedError("")
    
    def has_input(self):
        """boolean"""
        raise NotImplementedError("")
    
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        raise NotImplementedError("")
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element
        """
        raise NotImplementedError("")
        
    def do_processing(self, cg_steps):
        raise NotImplementedError("")
        
    def serialize(self):
        """
        Returns a dictionary of all of the current fields
        """
        args = self.arguments()
        vals = parse_arguments_from_element(self.element, args.keys())
        
        return {
            k:v for k,v in zip(args.keys(), vals)
        }

# Template version
class CopyThisOne(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return dict()
        
    def title(self):
        """String title"""
        return ""
    
    def has_input(self):
        """boolean"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element
        """
        raise NotImplementedError("")
        
    def do_processing(self, cg_steps):
        raise NotImplementedError("")

############################

class CG8ValueRecolor(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'black': '000000',
            'white': 'FFFFFF',
            'red': 'FF0000',
            'green': '00FF00',
            'blue': '0000FF',
            'yellow': 'FFFF00',
            'magenta': 'FF00FF',
            'cyan': '00FFFF',
        }
        
    def title(self):
        """String title"""
        return "8-Value Recolor"
    
    def has_input(self):
        """boolean"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element
        """
        args = {**self.arguments(), **parameters}
        
        for i,c in enumerate(args.keys()):
            # Line break if needed
            if (i%2)==0 and i>0:
                element.appendChild(create_element_with_tags("br"))
                
            add_input_field(
                self.element, c, f' {c.capitalize()}: ', args[c], size=4
            )
        
    def do_processing(self, cg_steps):
        cg_in = cg_steps[self.get_target_index()]
                
        colors = parse_arguments_from_element(self.element, self.arguments().keys())
        colors_scalar = [parse_color(c) for c in colors]
        cg_out = linear_recolor(cg_in, colors_scalar)
        
        return cg_out

class CGSimpleRecolor(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'black': '000000',
            'white': 'FFFFFF',
        }
        
    def title(self):
        """String title"""
        return "Simple Recolor"
    
    def has_input(self):
        """boolean"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element
        """
        args = {**self.arguments(), **parameters}
        
        for i,c in enumerate(args.keys()):
            add_input_field(
                self.element, c, f' {c.capitalize()}: ', args[c], size=4
            )
        
    def do_processing(self, cg_steps):
        cg_in = cg_steps[self.get_target_index()]
        
        colors = parse_arguments_from_element(self.element, ['black','white'])
        colors_scalar = [parse_color(c) for c in colors]
        cg_out = simple_recolor(cg_in, *colors_scalar)
        
        return cg_out

