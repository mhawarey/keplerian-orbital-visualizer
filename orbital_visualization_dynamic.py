import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import time
from matplotlib.widgets import Slider
import math

class DynamicOrbitalVisualizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Keplerian Orbital Visualization - By Dr. Mosab Hawarey")
        self.root.geometry("1200x800")
        
        # Top panel for title/header
        self.top_panel = tk.Frame(root, bg="#336699", height=50)
        self.top_panel.pack(side=tk.TOP, fill=tk.X)
        
        title_label = tk.Label(self.top_panel, text="Dynamic Keplerian Orbital Elements Visualizer - By Dr. Mosab Hawarey", 
                              bg="#336699", fg="white", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Main content area
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (1/3 width) for input fields
        self.left_panel = tk.Frame(self.content_frame, width=300, bd=2, relief=tk.GROOVE)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Right panel (2/3 width) for visualization
        self.right_panel = tk.Frame(self.content_frame, bd=2, relief=tk.GROOVE)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom panel for time controls
        self.bottom_panel = tk.Frame(root, bg="#336699", height=80)
        self.bottom_panel.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.setup_bottom_panel()
        
        # Setup the input fields
        self.setup_input_fields()
        
        # Setup the visualization area
        self.setup_visualization()
        
        # Add Calculate button
        self.calculate_button = tk.Button(self.left_panel, text="Calculate & Visualize Orbit", 
                                         command=self.update_visualization, bg="#4CAF50", fg="white",
                                         font=("Arial", 10, "bold"))
        self.calculate_button.grid(row=8, column=0, columnspan=2, pady=15, padx=10, sticky="ew")
        
        # Add Reset button
        self.reset_button = tk.Button(self.left_panel, text="Reset Fields", 
                                     command=self.reset_fields, bg="#f44336", fg="white",
                                     font=("Arial", 10, "bold"))
        self.reset_button.grid(row=9, column=0, columnspan=2, pady=5, padx=10, sticky="ew")
        
        # Animation variables
        self.anim = None
        self.satellite = None
        self.ground_track = None
        self.orbit_time = 0
        self.is_animating = False
        self.animation_speed = 1.0
        
        # Initial visualization
        self.update_visualization()
    
    def setup_input_fields(self):
        # Title for input section
        input_title = tk.Label(self.left_panel, text="Orbital Elements Input", font=("Arial", 12, "bold"))
        input_title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Input fields for Keplerian elements
        self.input_fields = {}
        
        # Define the Keplerian elements and their default values
        keplerian_elements = [
            ("a", "Semi-major axis (km)", 8000),
            ("e", "Eccentricity", 0.1),
            ("i", "Inclination (deg)", 45),
            ("Ω", "Right Ascension of Ascending Node (deg)", 30),
            ("ω", "Argument of Periapsis (deg)", 60),
            ("ν", "True Anomaly (deg)", 0)
        ]
        
        # Create input fields for each element
        for idx, (symbol, description, default) in enumerate(keplerian_elements):
            row = idx + 1
            
            # Label for the element
            label = tk.Label(self.left_panel, text=f"{description} ({symbol}):")
            label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            # Entry field for the value
            var = tk.StringVar(value=str(default))
            entry = tk.Entry(self.left_panel, textvariable=var, width=15)
            entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
            
            self.input_fields[symbol] = var
        
        # Add Earth rotation option
        self.show_ground_track = tk.BooleanVar(value=True)
        self.ground_track_check = tk.Checkbutton(self.left_panel, text="Show Ground Track", 
                                                variable=self.show_ground_track)
        self.ground_track_check.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Information text
        info_text = ("Enter the six Keplerian elements to define an orbit. "
                    "Click 'Calculate & Visualize' to update the plot. "
                    "Use the controls below to animate the orbit.")
        info_label = tk.Label(self.left_panel, text=info_text, wraplength=280, 
                             justify=tk.LEFT, fg="#555555")
        info_label.grid(row=10, column=0, columnspan=2, padx=10, pady=15, sticky="w")
        
        # Energy graph
        self.energy_frame = tk.Frame(self.left_panel, height=150, bd=1, relief=tk.SUNKEN)
        self.energy_frame.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        energy_title = tk.Label(self.energy_frame, text="Orbital Energy", font=("Arial", 10, "bold"))
        energy_title.pack(pady=5)
        
        self.energy_figure = Figure(figsize=(3, 2), dpi=100)
        self.energy_ax = self.energy_figure.add_subplot(111)
        self.energy_canvas = FigureCanvasTkAgg(self.energy_figure, self.energy_frame)
        self.energy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def setup_visualization(self):
        # Create a Figure and an Axes3D
        self.figure = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # Create the canvas for the plot
        self.canvas = FigureCanvasTkAgg(self.figure, self.right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.right_panel)
        self.toolbar.update()
    
    def setup_bottom_panel(self):
        # Time display
        self.time_label = tk.Label(self.bottom_panel, text="Elapsed Time: 0.00 hours", 
                                  bg="#336699", fg="white", font=("Arial", 10))
        self.time_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Period display
        self.period_label = tk.Label(self.bottom_panel, text="Orbital Period: N/A", 
                                    bg="#336699", fg="white", font=("Arial", 10))
        self.period_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Animation controls frame
        controls_frame = tk.Frame(self.bottom_panel, bg="#336699")
        controls_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Play/Pause button
        self.play_pause_button = tk.Button(controls_frame, text="▶ Play", 
                                          command=self.toggle_animation, width=8)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)
        
        # Reset animation button
        self.reset_anim_button = tk.Button(controls_frame, text="⟲ Reset", 
                                          command=self.reset_animation, width=8)
        self.reset_anim_button.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        speed_frame = tk.Frame(controls_frame, bg="#336699")
        speed_frame.pack(side=tk.LEFT, padx=10)
        
        speed_label = tk.Label(speed_frame, text="Speed:", bg="#336699", fg="white")
        speed_label.pack(side=tk.LEFT, padx=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = tk.Scale(speed_frame, from_=0.1, to=10.0, resolution=0.1, 
                              orient=tk.HORIZONTAL, variable=self.speed_var, 
                              command=self.update_speed, length=150, bg="#336699", fg="white")
        speed_scale.pack(side=tk.LEFT)
    
    def update_speed(self, event=None):
        self.animation_speed = self.speed_var.get()
    
    def toggle_animation(self):
        if self.anim is None:
            self.start_animation()
        elif self.is_animating:
            self.pause_animation()
        else:
            self.resume_animation()
    
    def start_animation(self):
        if self.anim is not None:
            self.anim.event_source.stop()
        
        self.orbit_time = 0
        self.is_animating = True
        self.play_pause_button.config(text="⏸ Pause")
        
        # Start the animation
        self.anim = animation.FuncAnimation(
            self.figure, self.animate_orbit, interval=50, 
            blit=False, save_count=100)
        
        self.canvas.draw()
    
    def pause_animation(self):
        if self.anim is not None:
            self.anim.event_source.stop()
            self.is_animating = False
            self.play_pause_button.config(text="▶ Play")
    
    def resume_animation(self):
        if self.anim is not None:
            self.anim.event_source.start()
            self.is_animating = True
            self.play_pause_button.config(text="⏸ Pause")
    
    def reset_animation(self):
        self.orbit_time = 0
        if self.anim is not None:
            self.pause_animation()
            self.update_satellite_position(0)
            self.time_label.config(text=f"Elapsed Time: 0.00 hours")
            self.canvas.draw()
    
    def calculate_orbital_period(self, a):
        """Calculate orbital period in hours using Kepler's Third Law"""
        # Earth's gravitational parameter in km^3/s^2
        mu = 398600.4418  
        # Period in seconds
        period_seconds = 2 * np.pi * np.sqrt(a**3 / mu)
        # Convert to hours
        return period_seconds / 3600
    
    def update_visualization(self):
        try:
            # Clear the current plot
            self.ax.clear()
            
            # Get the Keplerian elements from the input fields
            a = float(self.input_fields["a"].get())  # Semi-major axis (km)
            e = float(self.input_fields["e"].get())  # Eccentricity
            i = np.radians(float(self.input_fields["i"].get()))  # Inclination (rad)
            RAAN = np.radians(float(self.input_fields["Ω"].get()))  # Right Ascension of Ascending Node (rad)
            w = np.radians(float(self.input_fields["ω"].get()))  # Argument of Periapsis (rad)
            nu_start = np.radians(float(self.input_fields["ν"].get()))  # True Anomaly (rad)
            
            # Store the orbital elements for animation
            self.orbital_elements = {
                'a': a, 'e': e, 'i': i, 'RAAN': RAAN, 'w': w, 'nu_start': nu_start
            }
            
            # Validate inputs
            if e >= 1.0:
                messagebox.showerror("Input Error", "Eccentricity must be less than 1.0 for elliptical orbits")
                return
            
            if a <= 0:
                messagebox.showerror("Input Error", "Semi-major axis must be positive")
                return
            
            # Calculate orbital period
            period = self.calculate_orbital_period(a)
            self.orbital_period = period
            self.period_label.config(text=f"Orbital Period: {period:.2f} hours")
            
            # Calculate the orbit
            # Generate true anomaly values
            self.nu_values = np.linspace(0, 2*np.pi, 1000)
            
            # Calculate position vectors in the orbital plane
            r_values = a * (1 - e**2) / (1 + e * np.cos(self.nu_values))
            x_orbit = r_values * np.cos(self.nu_values)
            y_orbit = r_values * np.sin(self.nu_values)
            z_orbit = np.zeros_like(x_orbit)
            
            # Store for animation
            self.r_values = r_values
            
            # Rotation matrices
            # Rotation about the z-axis by the argument of periapsis
            R_w = np.array([
                [np.cos(w), -np.sin(w), 0],
                [np.sin(w), np.cos(w), 0],
                [0, 0, 1]
            ])
            
            # Rotation about the x-axis by the inclination
            R_i = np.array([
                [1, 0, 0],
                [0, np.cos(i), -np.sin(i)],
                [0, np.sin(i), np.cos(i)]
            ])
            
            # Rotation about the z-axis by the right ascension of ascending node
            R_RAAN = np.array([
                [np.cos(RAAN), -np.sin(RAAN), 0],
                [np.sin(RAAN), np.cos(RAAN), 0],
                [0, 0, 1]
            ])
            
            # Combined rotation matrix
            R = R_RAAN @ R_i @ R_w
            self.rotation_matrix = R
            
            # Apply rotations to get position vectors in the reference frame
            positions = np.zeros((3, len(self.nu_values)))
            for j in range(len(self.nu_values)):
                pos_orbit = np.array([x_orbit[j], y_orbit[j], z_orbit[j]])
                positions[:, j] = R @ pos_orbit
            
            self.x = positions[0, :]
            self.y = positions[1, :]
            self.z = positions[2, :]
            
            # Plot the orbit
            self.ax.plot(self.x, self.y, self.z, 'b-', linewidth=2, label='Orbit')
            
            # Highlight periapsis (nu = 0)
            periapsis_idx = 0
            self.ax.scatter(self.x[periapsis_idx], self.y[periapsis_idx], self.z[periapsis_idx], 
                           color='red', marker='o', s=100, label='Periapsis')
            
            # Highlight apoapsis (nu = pi)
            apoapsis_idx = len(self.nu_values) // 2
            self.ax.scatter(self.x[apoapsis_idx], self.y[apoapsis_idx], self.z[apoapsis_idx], 
                           color='green', marker='o', s=100, label='Apoapsis')
            
            # Draw Earth
            self.earth_radius = 6371  # km
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            earth_x = self.earth_radius * np.cos(u) * np.sin(v)
            earth_y = self.earth_radius * np.sin(u) * np.sin(v)
            earth_z = self.earth_radius * np.cos(v)
            self.earth = self.ax.plot_surface(earth_x, earth_y, earth_z, color='blue', alpha=0.3)
            
            # Add satellite point
            self.satellite = self.ax.scatter([], [], [], color='yellow', s=100)
            
            # Add ground track point if enabled
            if self.show_ground_track.get():
                self.ground_track_points = []
            
            # Plot coordinate axes
            max_range = max(np.max(np.abs(self.x)), np.max(np.abs(self.y)), np.max(np.abs(self.z)))
            axis_length = max_range * 0.25
            
            # x-axis (red)
            self.ax.plot([0, axis_length], [0, 0], [0, 0], 'r-', linewidth=2)
            # y-axis (green)
            self.ax.plot([0, 0], [0, axis_length], [0, 0], 'g-', linewidth=2)
            # z-axis (blue)
            self.ax.plot([0, 0], [0, 0], [0, axis_length], 'b-', linewidth=2)
            
            # Set labels and title
            self.ax.set_xlabel('X (km)')
            self.ax.set_ylabel('Y (km)')
            self.ax.set_zlabel('Z (km)')
            self.ax.set_title('Orbital Visualization')
            
            # Set equal aspect ratio
            max_range = max(np.max(np.abs(self.x)), np.max(np.abs(self.y)), np.max(np.abs(self.z)))
            self.ax.set_xlim(-max_range, max_range)
            self.ax.set_ylim(-max_range, max_range)
            self.ax.set_zlim(-max_range, max_range)
            
            # Add legend
            self.ax.legend()
            
            # Update the canvas
            self.canvas.draw()
            
            # Update the energy graph
            self.update_energy_graph()
            
            # Reset animation
            if self.anim is not None:
                self.anim.event_source.stop()
                self.anim = None
                self.play_pause_button.config(text="▶ Play")
                self.is_animating = False
                self.orbit_time = 0
                self.time_label.config(text=f"Elapsed Time: 0.00 hours")
            
            # Position satellite at starting point (using input true anomaly)
            self.update_satellite_position(nu_start)
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}\nPlease enter numeric values.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def update_energy_graph(self):
        """Update the orbital energy graph"""
        self.energy_ax.clear()
        
        # Earth's gravitational parameter (km^3/s^2)
        mu = 398600.4418
        
        a = self.orbital_elements['a']
        e = self.orbital_elements['e']
        
        # Calculate specific mechanical energy (constant for the orbit)
        specific_energy = -mu / (2 * a)
        
        # Calculate velocities at different points in the orbit
        velocities = []
        positions = []
        
        for nu in self.nu_values:
            # Distance from focus
            r = a * (1 - e**2) / (1 + e * np.cos(nu))
            
            # Velocity
            v = np.sqrt(mu * (2/r - 1/a))
            
            velocities.append(v)
            positions.append(r)
        
        # Plot velocity vs true anomaly
        self.energy_ax.plot(np.degrees(self.nu_values), velocities, 'r-')
        self.energy_ax.set_xlabel('True Anomaly (deg)')
        self.energy_ax.set_ylabel('Velocity (km/s)')
        self.energy_ax.grid(True)
        self.energy_ax.set_title(f'Specific Energy: {specific_energy:.2f} km²/s²')
        
        # Add markers for periapsis and apoapsis
        self.energy_ax.plot(0, velocities[0], 'ro', markersize=6)
        self.energy_ax.plot(180, velocities[len(velocities)//2], 'go', markersize=6)
        
        # Update the canvas
        self.energy_figure.tight_layout()
        self.energy_canvas.draw()
    
    def true_anomaly_to_mean_anomaly(self, nu, e):
        """Convert true anomaly to mean anomaly"""
        # Calculate eccentric anomaly
        cos_E = (e + np.cos(nu)) / (1 + e * np.cos(nu))
        sin_E = np.sqrt(1 - e**2) * np.sin(nu) / (1 + e * np.cos(nu))
        E = np.arctan2(sin_E, cos_E)
        
        # Calculate mean anomaly
        M = E - e * np.sin(E)
        
        return M
    
    def mean_anomaly_to_true_anomaly(self, M, e, tolerance=1e-8, max_iterations=100):
        """Convert mean anomaly to true anomaly using Newton-Raphson method"""
        # Initial guess for eccentric anomaly
        if M < np.pi:
            E = M + e/2
        else:
            E = M - e/2
        
        # Newton-Raphson iteration to solve Kepler's equation
        for i in range(max_iterations):
            E_next = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
            if abs(E_next - E) < tolerance:
                E = E_next
                break
            E = E_next
        
        # Calculate true anomaly from eccentric anomaly
        cos_nu = (np.cos(E) - e) / (1 - e * np.cos(E))
        sin_nu = np.sqrt(1 - e**2) * np.sin(E) / (1 - e * np.cos(E))
        nu = np.arctan2(sin_nu, cos_nu)
        
        # Ensure nu is between 0 and 2π
        if nu < 0:
            nu += 2 * np.pi
        
        return nu
    
    def time_to_true_anomaly(self, time_hours):
        """Convert time to true anomaly"""
        # Get orbital elements
        a = self.orbital_elements['a']
        e = self.orbital_elements['e']
        nu_start = self.orbital_elements['nu_start']
        
        # Earth's gravitational parameter (km^3/s^2)
        mu = 398600.4418
        
        # Calculate mean motion (rad/s)
        n = np.sqrt(mu / a**3)
        
        # Convert to rad/hour
        n_hours = n * 3600
        
        # Get initial mean anomaly
        M_start = self.true_anomaly_to_mean_anomaly(nu_start, e)
        
        # Calculate current mean anomaly
        M = M_start + n_hours * time_hours
        
        # Ensure M is between 0 and 2π
        M = M % (2 * np.pi)
        
        # Calculate current true anomaly
        nu = self.mean_anomaly_to_true_anomaly(M, e)
        
        return nu
    
    def animate_orbit(self, frame):
        """Update the satellite position for animation"""
        if not self.is_animating:
            return
        
        # Update time (hours)
        time_step = 0.05 * self.animation_speed  # animation interval in hours
        self.orbit_time += time_step
        
        # Update display
        self.time_label.config(text=f"Elapsed Time: {self.orbit_time:.2f} hours")
        
        # Calculate current true anomaly
        nu = self.time_to_true_anomaly(self.orbit_time)
        
        # Update satellite position
        self.update_satellite_position(nu)
        
        # If a complete orbit has been made, update ground track
        if self.orbit_time >= self.orbital_period:
            self.orbit_time = self.orbit_time % self.orbital_period
    
    def update_satellite_position(self, nu):
        """Update the satellite position for a given true anomaly"""
        try:
            # Get orbital elements
            a = self.orbital_elements['a']
            e = self.orbital_elements['e']
            
            # Calculate position in orbital plane
            r = a * (1 - e**2) / (1 + e * np.cos(nu))
            x_orb = r * np.cos(nu)
            y_orb = r * np.sin(nu)
            z_orb = 0
            
            # Transform to reference frame
            pos_orbital = np.array([x_orb, y_orb, z_orb])
            pos = self.rotation_matrix @ pos_orbital
            
            # Update satellite position
            self.satellite._offsets3d = ([pos[0]], [pos[1]], [pos[2]])
            
            # Update ground track if enabled
            if self.show_ground_track.get():
                # Calculate ground track (projection onto Earth's surface)
                r_sat = np.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
                scale_factor = self.earth_radius / r_sat
                ground_x = pos[0] * scale_factor
                ground_y = pos[1] * scale_factor
                ground_z = pos[2] * scale_factor
                
                # Add point to ground track
                ground_point = self.ax.scatter([ground_x], [ground_y], [ground_z], 
                                              color='orange', s=20, alpha=0.7)
                self.ground_track_points.append(ground_point)
                
                # Limit number of ground track points to prevent performance issues
                if len(self.ground_track_points) > 100:
                    old_point = self.ground_track_points.pop(0)
                    old_point.remove()
            
            # Find the closest index in the energy graph to highlight current position
            nu_deg = np.degrees(nu) % 360
            closest_idx = np.argmin(np.abs(np.degrees(self.nu_values) - nu_deg))
            
            # Update energy marker
            if hasattr(self, 'energy_marker'):
                self.energy_marker.remove()
            self.energy_marker = self.energy_ax.scatter(
                np.degrees(self.nu_values[closest_idx]), 
                np.sqrt(398600.4418 * (2/(self.r_values[closest_idx]) - 1/a)),
                color='blue', s=50, zorder=5
            )
            self.energy_canvas.draw()
            
            # Redraw canvas
            self.canvas.draw_idle()
            
        except Exception as e:
            print(f"Error updating satellite position: {str(e)}")
    
    def reset_fields(self):
        # Reset to default values
        defaults = {
            "a": "8000",
            "e": "0.1",
            "i": "45",
            "Ω": "30",
            "ω": "60",
            "ν": "0"
        }
        
        for key, value in defaults.items():
            self.input_fields[key].set(value)
        
        # Update the visualization
        self.update_visualization()


if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicOrbitalVisualizationApp(root)
    root.mainloop()