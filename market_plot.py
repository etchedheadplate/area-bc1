import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image
from data_tools import format_currency, convert_timestamp_to_utc, select_plot_background
from data_config import ticker, database_file, plot_path, plot_font, plot_background_image

df = pd.read_csv(database_file) # Load data from the CSV file

# Set the font properties for the text elements on the plot
custom_font = font_manager.FontProperties(fname=plot_font) # Use the specified font path

start_row = 1
end_row = 3800

fig, ax1 = plt.subplots(figsize=(10, 6)) # Create a figure and axes
fig.patch.set_alpha(0.0) # Set the background color inside the plot area to be transparent
ax2 = ax1.twinx() # Create a second y-axis on the right side

# Left y axis
line1, = ax1.plot( # line 1 creation
    df['Date'][start_row:end_row], # axis data from start row to end row
    df['Price'][start_row:end_row], # axis data from start row to end row
    color='orange', # line color
    label='Price', # line label
    linewidth=0.8, # line width
    zorder=1 # layer order (higher value puts layer to the front)
    )
ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: convert_timestamp_to_utc(x))) # x text format
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_currency(x, ticker))) # y text format
ax1.tick_params(axis='x', labelcolor='white') # x text color
ax1.tick_params(axis='y', labelcolor='orange') # y text color
ax1.set_zorder(2) # layer order (higher value puts layer to the front)

plt.setp(
    ax1.get_xticklabels(),
    rotation=30, # rotates text on x axis
    ha='right')  # alignes to right text on x axis

# Right y axis
line2, = ax2.plot( # line 1 creation
    df['Date'][start_row:end_row], # axis data from start row to end row
    df['Total Volumes'][start_row:end_row], # axis data from start row to end row
    color='green', # line color
    label='Total Volumes', # line label
    alpha=0.5, # line transparency
    linewidth=0.5, # line width
    )
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_currency(x, ticker))) # y text format
ax2.tick_params(axis='y', labelcolor='green') # y text color
ax2.set_zorder(1) # layer order (higher value puts layer to the front)
ax2.fill_between( # color filling of shape below the line
    df['Date'][start_row:end_row],
    df['Total Volumes'][start_row:end_row],
    color='green', # filling color
    alpha=0.1, # filling transparency
)

# Legend
legend = ax1.legend(
    [line1, line2], # lines in legend
    ['Price, $', 'Volume, $'], # titles of lines
    loc='upper left', # legend location
    prop=custom_font, # legend font
    handlelength=0
    )
legend.get_texts()[0].set_color('orange')
legend.get_texts()[1].set_color('green')
legend.get_frame().set_facecolor('white')  # Set the background color
legend.get_frame().set_alpha(0.1) 


# Set font properties for tick labels on both axes
for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
    label.set_fontproperties(custom_font)

ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.7) # Add gridlines to the plot
fig.patch.set_facecolor('none') # Set transparent background outside the plot area
dpi_value = 150 # Set DPI for plot image

plt.savefig(plot_path, bbox_inches='tight', transparent=True, dpi=dpi_value) # Save the plot to a PNG file with a transparent background

background = Image.open('src/images/backgrounds/good.png') # Open background image
overlay = Image.open(plot_path) # Open plot image
x = 750  # X-coordinate for plot image
y = 85  # Y-coordinate for plot image
background.paste(overlay, (x, y), overlay) # Paste plot image over background image
background.save("output.png") # Save the plot with background image