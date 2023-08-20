import matplotlib.colors
import matplotlib.pyplot as plt

def get_colorscheme(num_features):
    hsv = plt.get_cmap('hsv')
    offset = 0
    color_step = 255 // num_features
    colors = []
    for i in range(num_features):
        colors.append(matplotlib.colors.to_hex(hsv(i * color_step + offset)))
    return colors