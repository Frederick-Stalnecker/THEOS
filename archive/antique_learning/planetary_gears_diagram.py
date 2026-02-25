import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, Wedge
import numpy as np

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
ax.axis('off')

# Gear positions
gear_radius = 1.2
spacing_h = 2.8  # horizontal spacing
spacing_v = 2.8  # vertical spacing

# Positions: (x, y)
bottom_left = (-spacing_h/2, -spacing_v/2)
bottom_right = (spacing_h/2, -spacing_v/2)
top_left = (-spacing_h/2, spacing_v/2)
top_right = (spacing_h/2, spacing_v/2)

# Draw gears with color coding
# White = Clockwise (CW)
# Black = Counter-Clockwise (CCW)

def draw_gear(ax, center, radius, color, label, rotation_dir, num_teeth=12):
    """Draw a gear with teeth"""
    x, y = center
    
    # Main circle
    circle = Circle(center, radius, color=color, ec='black', linewidth=2, zorder=2)
    ax.add_patch(circle)
    
    # Draw teeth
    tooth_height = 0.15
    tooth_width = 2 * np.pi / num_teeth
    
    for i in range(num_teeth):
        angle = i * tooth_width
        tooth = Wedge(center, radius + tooth_height, 
                     np.degrees(angle - tooth_width/3), 
                     np.degrees(angle + tooth_width/3),
                     color=color, ec='black', linewidth=1, zorder=2)
        ax.add_patch(tooth)
    
    # Label
    label_color = 'white' if color == 'black' else 'black'
    ax.text(x, y, label, ha='center', va='center', 
            fontsize=10, fontweight='bold', color=label_color, zorder=3)
    
    # Rotation arrow
    arrow_radius = radius * 0.6
    if rotation_dir == 'CW':
        # Clockwise arrow
        angle_start = np.pi/4
        angle_end = -np.pi/4
        arrow_x1 = x + arrow_radius * np.cos(angle_start)
        arrow_y1 = y + arrow_radius * np.sin(angle_start)
        arrow_x2 = x + arrow_radius * np.cos(angle_end)
        arrow_y2 = y + arrow_radius * np.sin(angle_end)
        
        # Draw arc
        theta = np.linspace(angle_start, angle_end - 2*np.pi, 100)
        arc_x = x + arrow_radius * np.cos(theta)
        arc_y = y + arrow_radius * np.sin(theta)
        ax.plot(arc_x, arc_y, color=label_color, linewidth=2, zorder=3)
        
        # Arrowhead
        ax.annotate('', xy=(arrow_x2, arrow_y2), 
                   xytext=(arrow_x2 + 0.15, arrow_y2 - 0.15),
                   arrowprops=dict(arrowstyle='->', color=label_color, lw=2), zorder=3)
    else:
        # Counter-clockwise arrow
        angle_start = -np.pi/4
        angle_end = np.pi/4
        arrow_x1 = x + arrow_radius * np.cos(angle_start)
        arrow_y1 = y + arrow_radius * np.sin(angle_start)
        arrow_x2 = x + arrow_radius * np.cos(angle_end)
        arrow_y2 = y + arrow_radius * np.sin(angle_end)
        
        # Draw arc
        theta = np.linspace(angle_start, angle_end + 2*np.pi, 100)
        arc_x = x + arrow_radius * np.cos(theta)
        arc_y = y + arrow_radius * np.sin(theta)
        ax.plot(arc_x, arc_y, color=label_color, linewidth=2, zorder=3)
        
        # Arrowhead
        ax.annotate('', xy=(arrow_x2, arrow_y2), 
                   xytext=(arrow_x2 - 0.15, arrow_y2 - 0.15),
                   arrowprops=dict(arrowstyle='->', color=label_color, lw=2), zorder=3)

# Draw the four gears
draw_gear(ax, bottom_left, gear_radius, 'white', 'BL\nCW', 'CW')
draw_gear(ax, bottom_right, gear_radius, 'black', 'BR\nCCW', 'CCW')
draw_gear(ax, top_left, gear_radius, 'black', 'TL\nCCW', 'CCW')
draw_gear(ax, top_right, gear_radius, 'white', 'TR\nCW', 'CW')

# Draw mesh connection lines (light gray to show gear meshing)
mesh_color = '#CCCCCC'
mesh_width = 8

# Horizontal meshes
ax.plot([bottom_left[0] + gear_radius, bottom_right[0] - gear_radius], 
        [bottom_left[1], bottom_right[1]], 
        color=mesh_color, linewidth=mesh_width, zorder=1, alpha=0.5)
ax.plot([top_left[0] + gear_radius, top_right[0] - gear_radius], 
        [top_left[1], top_right[1]], 
        color=mesh_color, linewidth=mesh_width, zorder=1, alpha=0.5)

# Vertical meshes
ax.plot([bottom_left[0], top_left[0]], 
        [bottom_left[1] + gear_radius, top_left[1] - gear_radius], 
        color=mesh_color, linewidth=mesh_width, zorder=1, alpha=0.5)
ax.plot([bottom_right[0], top_right[0]], 
        [bottom_right[1] + gear_radius, top_right[1] - gear_radius], 
        color=mesh_color, linewidth=mesh_width, zorder=1, alpha=0.5)

# Input arrows (horizontal - left and right)
arrow_props = dict(arrowstyle='->', lw=3, color='blue')

# Left input
ax.annotate('', xy=(-spacing_h/2 - gear_radius - 0.3, 0), 
           xytext=(-spacing_h/2 - gear_radius - 1.2, 0),
           arrowprops=arrow_props)
ax.text(-spacing_h/2 - gear_radius - 1.5, 0, 'INPUT\n(Query)', 
        ha='center', va='center', fontsize=11, fontweight='bold', color='blue')

# Right input (optional/feedback)
ax.annotate('', xy=(spacing_h/2 + gear_radius + 1.2, 0), 
           xytext=(spacing_h/2 + gear_radius + 0.3, 0),
           arrowprops=dict(arrowstyle='->', lw=2, color='blue', linestyle='dashed'))
ax.text(spacing_h/2 + gear_radius + 1.6, 0, 'FEEDBACK\n(Optional)', 
        ha='center', va='center', fontsize=9, color='blue', style='italic')

# Output arrows (vertical - top and bottom)
output_props = dict(arrowstyle='->', lw=3, color='green')

# Bottom output
ax.annotate('', xy=(0, -spacing_v/2 - gear_radius - 1.2), 
           xytext=(0, -spacing_v/2 - gear_radius - 0.3),
           arrowprops=output_props)
ax.text(0, -spacing_v/2 - gear_radius - 1.6, 'OBJECT OUTPUT\n(Answer)', 
        ha='center', va='center', fontsize=11, fontweight='bold', color='green')

# Top output
ax.annotate('', xy=(0, spacing_v/2 + gear_radius + 1.2), 
           xytext=(0, spacing_v/2 + gear_radius + 0.3),
           arrowprops=output_props)
ax.text(0, spacing_v/2 + gear_radius + 1.6, 'META OUTPUT\n(Reasoning Trace)', 
        ha='center', va='center', fontsize=11, fontweight='bold', color='green')

# Add labels for layers
ax.text(-4.2, spacing_v/2, 'META\nLAYER', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='purple',
        bbox=dict(boxstyle='round', facecolor='lavender', alpha=0.7))
ax.text(-4.2, -spacing_v/2, 'OBJECT\nLAYER', ha='center', va='center', 
        fontsize=10, fontweight='bold', color='purple',
        bbox=dict(boxstyle='round', facecolor='lavender', alpha=0.7))

# Add axis labels
ax.text(0, -4.5, 'HORIZONTAL AXIS: Dialectical Contradiction', 
        ha='center', va='center', fontsize=12, fontweight='bold', color='red')
ax.text(-4.5, 0, 'VERTICAL\nAXIS:\nRefinement\n&\nSynthesis', 
        ha='center', va='center', fontsize=12, fontweight='bold', color='darkgreen',
        rotation=90)

# Title
ax.text(0, 4.5, 'THEOS Planetary Dialectical System\nFour-Gear Cross-Flow Architecture', 
        ha='center', va='center', fontsize=14, fontweight='bold')

# Legend
legend_x = 3.5
legend_y = -3.5
ax.text(legend_x, legend_y, 'WHITE = Clockwise (CW)\nBLACK = Counter-Clockwise (CCW)', 
        ha='left', va='top', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('/home/ubuntu/THEOS/planetary_dialectical_system.png', dpi=300, bbox_inches='tight')
print("Diagram saved to: /home/ubuntu/THEOS/planetary_dialectical_system.png")
