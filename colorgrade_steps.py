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

def add_input_field_args(parent, name, label, args, **kwargs):
    add_input_field(parent, name, label, args[name], **kwargs)

### Abstract class

class ColorgradeProcessStep:
    """
    Template class for a colorgrade processing step.
    """
    def __init__(self, process_id, element, process_type_internal):
        """
        Creates a new process step
        """
        self.process_id = process_id
        self.element = element
        self.process_type_internal = process_type_internal
    
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
        
        return process_type_internal, {
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
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        raise NotImplementedError("")
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        cg_in = cg_steps[self.get_target_index()]
        
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

class CGRecenterColors(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return dict()
        
    def title(self):
        """String title"""
        return "Recenter Colors"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element
        """
        # This has no additional fields
        pass
        
    def do_processing(self, cg_steps):
        cg_in = cg_steps[self.get_target_index()]
        return rescale_to_fill_range(cg_in)
        
class CGFill(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return dict(color='FFFFFF')
        
    def title(self):
        """String title"""
        return "Fill"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return False
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element
        """
        args = {**self.arguments(), **parameters}
        add_input_field(element, 'color', 'Color: ', args['color'], size=4)
        
    def do_processing(self, cg_steps):
        color = parse_color(
            parse_arguments_from_element(
                self.element,
                ['color']
            )[0]
        )
        return get_filled_colorgrade(color)

class CGIfElse(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'condition': 'r+g+b > 0.5',
            'cond-input': '0',
            'true-input': '-1',
            'false-input': '-1',
        }
        
    def title(self):
        """String title"""
        return "If-Else"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return False
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        
        add_input_field(element, 'condition', ' Condition: ', args['condition'], size=24)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'cond-input', 'Condition source: ', args['cond-input'], size=2)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'true-input', 'Source if true: ', args['true-input'], size=2)
        element.appendChild(create_element_with_tags("br"))
        add_input_field(element, 'false-input', 'Source if false: ', args['false-input'], size=2)
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        condition, cond_idx, true_idx, false_idx = parse_arguments_from_element(
            self.element,
            ['condition', 'cond-input', 'true-input', 'false-input']
        )
        cg_true = cg_steps[int(true_idx)]
        cg_false = cg_steps[int(false_idx)]
        cg_cond = cg_steps[int(cond_idx)]
        
        return if_else(cg_true, cg_false, cg_cond, condition)
        
class CGAdjustRGB(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'r-shift': '0.0',
            'g-shift': '0.0',
            'b-shift': '0.0',
        }
        
    def title(self):
        """String title"""
        return "Adjust RGB"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        
        add_input_field_args(element, 'r-shift', ' R shift: ', args, size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 'g-shift', ' G shift: ', args, size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 'b-shift', ' B shift: ', args, size=4)
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        cg_in = cg_steps[self.get_target_index()]
        
        shifts = [
            float(val)
            for val in parse_arguments_from_element(
                self.element,
                ['r-shift', 'g-shift', 'b-shift']
            )
        ]
        
        return adjust_rgb(cg_in, *shifts)

class CGAdjustHSV(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'h-shift': '0.0',
            's-shift': '0.0',
            'v-shift': '0.0',
        }
        
    def title(self):
        """String title"""
        return "Adjust HSV"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        
        add_input_field_args(element, 'h-shift', ' H shift: ', args, size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 's-shift', ' S shift: ', args, size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 'v-shift', ' V shift: ', args, size=4)
        
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        cg_in = cg_steps[self.get_target_index()]
        
        shifts = [
            float(val)
            for val in parse_arguments_from_element(
                self.element,
                ['h-shift', 's-shift', 'v-shift']
            )
        ]
        
        return adjust_hsv(cg_in, *shifts)

class CGBrightnessContrast(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'bright-shift': '0.0',
            'con-shift': '0.0',
        }
        
    def title(self):
        """String title"""
        return "Brightness/Contrast"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        add_input_field_args(element, 'bright-shift', ' Brightness: ', args, size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 'con-shift', ' Contrast: ', args, size=4)
    
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        cg_in = cg_steps[self.get_target_index()]
        
        shifts = [
            float(val)
            for val in parse_arguments_from_element(
                self.element,
                ['bright-shift', 'con-shift']
            )
        ]
        
        return brightness_contrast(cg_in, *shifts)

class CGCustomMap(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'new-r': 'r',
            'new-g': 'g',
            'new-b': 'b',
        }
        
    def title(self):
        """String title"""
        return "Custom"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        add_input_field_args(element, 'new-r', ' New R: ', args, size=24)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 'new-g', ' New G: ', args, size=24)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 'new-b', ' New B: ', args, size=24)
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        cg_in = cg_steps[self.get_target_index()]
        
        expressions = parse_arguments_from_element(
            self.element,
            ['new-r', 'new-g', 'new-b']
        )
        
        return custom_rgb_adjust(cg_in, *expressions)

class CGPalettize(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'colors': '000000; FFFFFF'
        }
        
    def title(self):
        """String title"""
        return "Palettize"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        add_input_field_args(element, 'colors', ' Colors: ', args, size=26)
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        cg_in = cg_steps[self.get_target_index()]
        
        color_string = parse_arguments_from_element(
            self.element,
            ['colors']
        )[0].split(';')
        
        colors = [
            parse_color(s.strip()) for s in color_string if len(s.strip()) > 0
        ]
        
        return palettize(cg_in, colors)

class CGReduceColors(ColorgradeProcessStep):
    def arguments(self):
        """
        Return a dictionary of the input things and their default values
        """
        return {
            'n-colors': '10',
            'seed': '97187',
        }
        
    def title(self):
        """String title"""
        return "Reduce Colors"
    
    def has_input(self):
        """boolean of whether it accepts a single previous step as input"""
        return True
    
    def populate_html_element(self, element, **parameters):
        """
        Add input fields to the element (modify in-place).
        Does not need to return anything.
        """
        args = {**self.arguments(), **parameters}
        add_input_field_args(element, 'n-colors', ' # Colors: ', args, size=4)
        element.appendChild(create_element_with_tags("br"))
        add_input_field_args(element, 'seed', ' Random seed: ', args, size=8)
        
    def do_processing(self, cg_steps):
        """
        Return the result of this step
        """
        cg_in = cg_steps[self.get_target_index()]
        
        n_colors, seed = [
            int(val)
            for val in parse_arguments_from_element(
                self.element,
                ['n-colors', 'seed']
            )
        ]
        
        return reduce_colors(cg_in, n_colors, seed=seed)

