import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math_utils import cartesian_to_polar, polar_to_cartesian, shift_coordinates


def to_cartesian(r_to_handlebar, theta_to_handlebar, r_to_bottom_bracket, theta_to_bottom_bracket):
    """
    Converts polar coordinates to Cartesian coordinates for handlebar and bottom bracket.
    Uses functions from `coordinate_conversion.py`.
    """
    handlebar_x, handlebar_y = polar_to_cartesian(r_to_handlebar, theta_to_handlebar, is_clockwise=True)
    bottom_bracket_x, bottom_bracket_y = polar_to_cartesian(r_to_bottom_bracket, theta_to_bottom_bracket, is_clockwise=True)

    # Shift coordinates so that the bottom bracket is at (0,0)
    handlebar_x, handlebar_y = shift_coordinates(handlebar_x, handlebar_y, bottom_bracket_x, bottom_bracket_y)
    saddle_x, saddle_y = shift_coordinates(0, 0, bottom_bracket_x, bottom_bracket_y)

    return handlebar_x, handlebar_y, saddle_x, saddle_y


def to_polar(handlebar_x, handlebar_y, saddle_x, saddle_y):
    """
    Converts Cartesian coordinates to polar coordinates using `cartesian_to_polar` from `coordinate_conversion.py`.
    """
    # Move coordinate system so the saddle is at (0,0)
    handlebar_x, handlebar_y = shift_coordinates(handlebar_x, handlebar_y, saddle_x, saddle_y)
    bottom_bracket_x, bottom_bracket_y = shift_coordinates(0, 0, saddle_x, saddle_y)

    r_to_handlebar, theta_to_handlebar = cartesian_to_polar(handlebar_x, handlebar_y, is_clockwise=True)
    r_to_bottom_bracket, theta_to_bottom_bracket = cartesian_to_polar(bottom_bracket_x, bottom_bracket_y, is_clockwise=True)

    return r_to_handlebar, theta_to_handlebar, r_to_bottom_bracket, theta_to_bottom_bracket


def fill_missing_coordinates(row):
    """
    Fills missing Cartesian or Polar coordinates in a row.
    If Cartesian coordinates are missing, calculates them from Polar.
    If Polar coordinates are missing, calculates them from Cartesian.
    Finally, shifts coordinate system to the saddle.
    """
    
    # Case 1: If Cartesian coordinates are missing → Convert from Polar
    if pd.isna(row["handlebar_x"]) or pd.isna(row["saddle_x"]):
        row["handlebar_x"], row["handlebar_y"], row["saddle_x"], row["saddle_y"] = to_cartesian(
            row["r_to_handlebar"], row["theta_to_handlebar"], row["r_to_bottom_bracket"], row["theta_to_bottom_bracket"]
        )

    # Case 2: If Polar coordinates are missing → Convert from Cartesian
    if pd.isna(row["r_to_handlebar"]) or pd.isna(row["theta_to_handlebar"]):
        row["r_to_handlebar"], row["theta_to_handlebar"], row["r_to_bottom_bracket"], row["theta_to_bottom_bracket"] = to_polar(
            row["handlebar_x"], row["handlebar_y"], row["saddle_x"], row["saddle_y"]
        )

    # Shift coordinate system so that the saddle is the new origin
    row['s_handlebar_x'], row['s_handlebar_y'] = shift_coordinates(row["handlebar_x"], row["handlebar_y"], row['saddle_x'], row['saddle_y'])
    row['s_bottom_bracket_x'], row['s_bottom_bracket_y'] = shift_coordinates(0, 0, row['saddle_x'], row['saddle_y'])

    return row





def plot_cartesian(handlebar_x, handlebar_y, saddle_x, saddle_y):
    """
    Plots the bike fit setup in Cartesian coordinates.
    """
    plt.figure(figsize=(8, 6))

    plt.scatter(handlebar_x, handlebar_y, color="blue", label="Handlebar", s=100, edgecolor="black")
    plt.scatter(saddle_x, saddle_y, color="red", label="Saddle", s=100, edgecolor="black")
    plt.scatter(0, 0, color="green", marker="x", s=150, label="Bottom Bracket")

    plt.xlabel("X (mm)")
    plt.ylabel("Y (mm)")
    plt.legend(title="Bike Parts")
    plt.title("Bike Fit - Cartesian Coordinate System")
    plt.grid(True)
    plt.gca().set_aspect("equal", adjustable="box")
    return plt


def plot_polar(r_to_handlebar, theta_to_handlebar, r_to_bottom_bracket, theta_to_bottom_bracket):
    """
    Plots the bike fit setup in Polar coordinates.
    """
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111, projection="polar")

    theta_to_handlebar_rad = np.radians(-theta_to_handlebar)
    theta_to_bottom_bracket_rad = np.radians(-theta_to_bottom_bracket)

    ax.scatter(theta_to_handlebar_rad, r_to_handlebar, color="blue", label="Handlebar", s=120)
    ax.scatter(theta_to_bottom_bracket_rad, r_to_bottom_bracket, color="red", label="Bottom Bracket", s=120)
    ax.scatter(0, 0, color="green", marker="x", s=150, label="Saddle")

    ax.set_title("Bike Fit - Polar Coordinate System")
    ax.legend(title="Bike Parts")

    return plt

def plot_bike_geometry(bike_data, center='bottom_bracket'):
    """
    Plots bike fitting geometry in Cartesian coordinates with an option to change the center.
    
    Parameters:
        bike_data (pd.DataFrame): The dataset containing bike geometry.
        center (str): The reference point for the coordinate system ('bottom_bracket' or 'saddle').
    """
    palette = sns.color_palette('tab10', n_colors=len(bike_data["Bike Name"].unique()))
    
    if center == 'saddle':
        x_handlebar, y_handlebar = "s_handlebar_x", "s_handlebar_y"
        x_bottom_bracket, y_bottom_bracket = "s_bottom_bracket_x", "s_bottom_bracket_y"
        zero_label = 'Saddle (0,0)'
    else:
        x_handlebar, y_handlebar = "handlebar_x", "handlebar_y"
        x_bottom_bracket, y_bottom_bracket = "saddle_x", "saddle_y"
        zero_label = 'Bottom Bracket (0,0)'
    
    sns.scatterplot(
        x=x_handlebar, y=y_handlebar,
        hue="Bike Name", style="Bike Name",
        data=bike_data, legend="full",
        edgecolor='black', s=120, palette=palette
    )
    
    sns.scatterplot(
        x=x_bottom_bracket, y=y_bottom_bracket,
        hue="Bike Name", style="Bike Name",
        data=bike_data, legend=False,
        edgecolor='black', s=120, palette=palette
    )
    
    plt.scatter([0], [0], color='black', marker='+', s=150, label=zero_label)
    plt.text(15, -45 if center == 'saddle' else 15, zero_label, color='black', ha='left', va='bottom')
    
    plt.legend(title="Models", loc='lower left', bbox_to_anchor=(0, 0.3))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    plt.xlabel('')
    plt.ylabel('')
    
    return plt


if __name__ == "__main__":
    # Load bike data from file
    bike_data = pd.read_csv("bike_data.csv")

    # Apply transformation to fill missing values
    bike_data = bike_data.apply(fill_missing_coordinates, axis=1)

    first = bike_data.iloc[0]

    plot_cartesian(first['handlebar_x'], first['handlebar_y'], first['saddle_x'], first['saddle_y']).show()

    plot_polar(first['r_to_handlebar'], first['theta_to_handlebar'], first['r_to_bottom_bracket'], first['theta_to_bottom_bracket']).show()

    plot_bike_geometry(bike_data, center='bottom_bracket').show()

    plot_bike_geometry(bike_data, center='saddle').show()

