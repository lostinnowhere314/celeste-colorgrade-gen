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
    # First, check if it's comma-separated float values
    if color_str.count(',') == 2:
        return tuple(float(v) for v in color_str.split(','))
    else:
        # Should be a hex string
        assert len(color_str) == 6, 'invalid input string'
        return tuple(
            int(f"0x{color_str[2*i:2*i+2]}", base=16) / 255 for i in range(3)
        )
        
def rgb_to_hsv(colors):
    """
    Based on https://www.rapidtables.com/convert/color/rgb-to-hsv.html
    Only works on a whole colorgrade
    """
    r, g, b = sep_rgb(np.array(colors))
    
    c_max = np.max(colors, axis=-1)
    c_min = np.min(colors, axis=-1)
    
    delta = c_max - c_min
    delta[delta == 0] = -1
    
    # Hue
    h = np.empty_like(r)
    h[r == c_max] = 60 * (((g[r == c_max] - b[r == c_max]) / delta[r == c_max]) % 6.)
    h[g == c_max] = 60 * (((b[g == c_max] - r[g == c_max]) / delta[g == c_max])) + 120
    h[b == c_max] = 60 * (((r[b == c_max] - g[b == c_max]) / delta[b == c_max])) + 240
    
    h[delta < 0] = 0.
    
    # Saturation
    delta[delta < 0] = 0
    c_max_denom = c_max.copy()
    c_max_denom[c_max == 0] = 1.
    s = delta / c_max_denom
    
    # Value
    v = c_max
    
    return np.stack((h, s, v), axis=3)
    
def hsv_to_rgb(colors):
    """
    Based on https://www.rapidtables.com/convert/color/hsv-to-rgb.html
    Only works on a whole colorgrade
    """    
    h, s, v = sep_rgb(np.array(colors))
    
    # Ensure h is in the right range
    h = h % 360
    
    c = v * s
    x = c * (1 - np.abs((h/60) % 2 - 1))
    m = np.expand_dims(v - c, axis=3)
    
    result = np.zeros_like(colors)
    hue_section = (h//60).astype(int)
    
    ## Lots of cases
    mask = hue_section == 0
    result[mask, 0] = c[mask]
    result[mask, 1] = x[mask]
    
    mask = hue_section == 1
    result[mask, 1] = c[mask]
    result[mask, 0] = x[mask]
    
    mask = hue_section == 2
    result[mask, 1] = c[mask]
    result[mask, 2] = x[mask]
    
    mask = hue_section == 3
    result[mask, 2] = c[mask]
    result[mask, 1] = x[mask]
    
    mask = hue_section == 4
    result[mask, 2] = c[mask]
    result[mask, 0] = x[mask]
    
    mask = hue_section == 5
    result[mask, 0] = c[mask]
    result[mask, 2] = x[mask]
    
    # Add the minimum
    result += m
    
    return result
    
def commutative_map(vals, a, vmin=0, vmax=1):
    """
    Applies a map to the range [vmin, vmax], maintaining anything outside as-is.
    Positive values of `a` increase values towards vmax, while negative values decrease towards vmin.
    
    These mappings form an abelian group of functions with respect to the parameter `a`, isomorphic to R;
    that is, a=0 will do nothing, negating a will have the inverse effect, and it is commutative 
    with respect to repeated applications. Mostly this just means that this will behave "nicely", 
    particularly with respect to using it multiple times.
    """
    mask = (vals >= vmin) & (vals <= vmax)
    if vmin == vmax:
        # Don't do anything
        return vals.copy()
    scaled = (vals[mask] - vmin) / (vmax - vmin) 
    
    scaled_result = scaled ** np.exp(-a / 10)
    
    result = vals.copy()
    result[mask] = scaled_result * (vmax - vmin) + vmin
    
    return result
    
def centered_commutative_map(vals, a, vmin=0, vmax=1):
    """
    Applies a map to the range [vmin, vmax], maintaining anything outside as-is.
    Positive values of `a` push values towards vmin and vmax, while negative values push
    towards the center of the range.
    
    These mappings form an abelian group of functions with respect to the parameter `a`, isomorphic to R;
    that is, a=0 will do nothing, negating a will have the inverse effect, and it is commutative 
    with respect to repeated applications. Mostly this just means that this will behave "nicely", 
    particularly with respect to using it multiple times.
    """
    mask = (vals >= vmin) & (vals <= vmax)
    if vmin == vmax:
        # Don't do anything
        return vals.copy()
    scaled = 2 * (vals[mask] - vmin) / (vmax - vmin) - 1
    
    scaled_result = np.abs(scaled) ** np.exp(-a / 10) * np.sign(scaled)
    
    result = vals.copy()
    result[mask] = (scaled_result + 1) * (vmax - vmin) / 2 + vmin
    
    return result
    
# Functions pertaining to evaluating expressions
def get_comparison_func(orig_fun):
    def new_fun(*args):
        # Determine if there are any arrays
        which_arrays = [not np.isscalar(a) for a in args]
        needs_vectorize = np.any(which_arrays)
        if needs_vectorize:
            # Find an array
            shape = args[np.argmax(which_arrays)].shape
            # Broadcast properly
            return orig_fun([np.full(shape, val) if np.isscalar(val) else val for val in args], axis=0)
        else:
            return orig_fun(args)
    
    return new_fun

# Provided functions/constants
eval_globals = dict(
    pi=np.pi,
    min=get_comparison_func(np.min),
    max=get_comparison_func(np.max),
    abs=np.abs,
    clip=np.clip,
    sin=np.sin,
    cos=np.cos,
    tan=np.tan,
    sqrt=np.sqrt,
    exp=np.exp,
    ln=np.log,
    log=np.log,
    log2=np.log2,
    log10=np.log10,
)

def eval_with(expression, _result_shape=None, **kwargs):
    """
    Evaluates a string expression with the given arguments as locals
    """
    result = eval(expression, eval_globals, {**eval_globals, **kwargs})
    if _result_shape is not None and np.isscalar(result):
        return np.full(_result_shape, result)
    else:
        return result
    
# Effects

def simple_recolor(cg, c_black, c_white):
    """
    Recolors black and white to the given colors
    """
    
    c_black = np.array(c_black).reshape(1,1,1,-1)
    c_white = np.array(c_white).reshape(1,1,1,-1)
    
    result = cg * (c_white - c_black) + c_black
    
    return result
    
def rescale_to_fill_range(cg):
    """
    Rescales a colorgrade so that the r,g,b values each extend over the whole range [0,1]
    """
    max_c = np.max(cg, axis=(0,1,2), keepdims=True)
    min_c = np.min(cg, axis=(0,1,2), keepdims=True)
    delta = max_c - min_c
    delta[delta == 0] = 1
    
    return (cg - min_c) / delta

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
    
def get_filled_colorgrade(color):
    """
    Returns a colorgrade filled with the given color
    """
    return np.zeros((16,16,16,3)) + np.array(color).reshape(1,1,1,3)
    
def if_else(cg1, cg2, cond_cg, condition):
    """
    Returns a new colorgrade with the color of `cg1` everywhere the condition is true for the condition colorgrade,
    and `cg2` everywhere else
    """
    # Evaluate the condition
    cr, cg, cb = sep_exp_rgb(cond_cg)
    mask = eval_with(condition, r=cr, g=cg, b=cb)
    # Use it to combine the colorgrades
    result = cg1 * mask + cg2 * (~mask)
    return result
    
def adjust_rgb(cg, r_shift, g_shift, b_shift):
    """
    Adjusts the rgb of a colorgrade
    """
    r, g, b = sep_rgb(cg)
    
    new_r = commutative_map(r, r_shift)
    new_g = commutative_map(g, g_shift)
    new_b = commutative_map(b, b_shift)
    
    return np.stack((new_r, new_g, new_b), axis=3)
    
def adjust_hsv(cg, hue_shift, sat_shift, val_shift):
    """
    Adjusts the hsv of a colorgrade
    """
    h, s, v = sep_rgb(rgb_to_hsv(cg))
    
    new_h = (h + hue_shift) % 360
    new_s = commutative_map(s, sat_shift)
    new_v = commutative_map(v, val_shift)
    
    new_hsv = np.stack((new_h, new_s, new_v), axis=3)
    
    return hsv_to_rgb(new_hsv)
    
def brightness_contrast(cg, bright_shift, con_shift):
    """
    Adjusts the hsv of a colorgrade
    """
    h, s, v = sep_rgb(rgb_to_hsv(cg))
    
    new_s = commutative_map(s, con_shift)
    new_v = centered_commutative_map(commutative_map(v, bright_shift), con_shift)
    
    new_hsv = np.stack((h, new_s, new_v), axis=3)
    
    return hsv_to_rgb(new_hsv)
    
def custom_rgb_adjust(cg, r_expr, g_expr, b_expr):
    expressions = [r_expr, g_expr, b_expr]
    
    r, g, b = sep_rgb(cg)
    
    result_colors = [
        eval_with(expr, r=r, g=g, b=b, shape=r.shape) for expr in expressions
    ]
    
    return np.stack(result_colors, axis=3)
    
def palletize(cg, colors, mode=None):
    raise NotImplementedError("")
    