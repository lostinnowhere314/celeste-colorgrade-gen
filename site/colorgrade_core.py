import numpy as np
## Utility functions for managing colorgrades

def get_default_colorgrade():
    """
    Creates the default colorgrade and returns it with color values as floats in [0,1], as an array of shape (16,16,16,3)
    """
    v = np.linspace(0,1,16)
    G,R,B = np.meshgrid(v,v,v)
    return np.stack((R,G,B), axis=3)

def sep_rgb(cg):
    return cg[:,:,:,0],cg[:,:,:,1],cg[:,:,:,2]
    
def sep_exp_rgb(cg):
    return np.expand_dims(cg[:,:,:,0],3), np.expand_dims(cg[:,:,:,1],3), np.expand_dims(cg[:,:,:,2],3)

def process_colorgrade(cg):
    """
    Transforms a colorgrade into a flat image with integer values to prepare to write to the canvas
    """
    return np.clip(
        255 * cg.transpose(1,2,0,3).reshape(16,256,3),
        0, 255
    ).transpose(1,0,2).astype(np.uint8)
    
def parse_color(color_str):
    """
    Converts a hex code to an rgb tuple
    TODO also support float values
    """
    assert len(color_str) == 6, 'invalid input string'
    return tuple(
        int(f"0x{color_str[2*i:2*i+2]}", base=16) / 255 for i in range(3)
    )
    
# Functions pertaining to evaluating expressions
def get_comparison_func(orig_fun):
    def new_fun(*args):
        which_arrays = [not np.isscalar(a) for a in args]
        needs_vectorize = np.any(which_arrays)
        if needs_vectorize:
            # Find an array
            shape = args[np.argmax(which_arrays)].shape
            return orig_fun([np.full(shape, val) for val in args if np.isscalar(val) else val])
        else:
            return orig_fun(args)
    
    return new_fun

# Provided functions
eval_functions = dict(
    min=get_comparison_func(np.min),
)
    
# Effects

def simple_recolor(cg, c_black, c_white):
    """
    Recolors black and white to the given colors
    """
    
    c_black = np.array(c_black).reshape(1,1,1,-1)
    c_white = np.array(c_black).reshape(1,1,1,-1)
    
    result = cg * (c_white - c_black) + c_black
    
    return result

def linear_recolor(cg, colors):
    """
    Recolors the eight corners of the color cube to the given colors,
    interpolated multilinearly.
    """
    c_black, c_white, c_red, c_green, c_blue, c_yellow, c_magenta, c_cyan = [np.array(c).reshape(1,1,1,-1) for c in colors]
    
    r, g, b = sep_exp_rgb(cg)
    
    result = (
        c_black * (1-r)*(1-g)*(1-b)
        + c_red * r*(1-g)*(1-b)
        + c_green * (1-r)*g*(1-b)
        + c_blue * (1-r)*(1-g)*b
        + c_yellow * r*g*(1-b)
        + c_cyan * (1-r)*g*b
        + c_magenta * r*(1-g)*b
        + c_white * r*g*b
    )
    
    return result

