# Buckminster Fusion

A Fusion 360 add-in for creating parametric geodesic spheres (Buckminster Fuller domes).

## Overview

This add-in generates geodesic spheres using icosahedron subdivision, allowing you to create precise geodesic dome structures directly in Fusion 360. Named in honor of Buckminster Fuller, the architect and designer who popularized geodesic dome structures.

## Features

- **Parametric geodesic sphere generation** using icosahedron subdivision
- **Adjustable frequency** for controlling the complexity of the dome
- **Customizable radius** for different dome sizes
- **Clean, triangulated mesh** suitable for structural analysis and fabrication
- Integrated into Fusion 360's CREATE panel for easy access

## Installation

1. Download or clone this repository
2. Copy the `BuckminsterFusion` folder to your Fusion 360 add-ins directory:
   - **Windows**: `%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - **macOS**: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
3. Launch Fusion 360
4. Go to **Tools** → **Add-Ins** → **Scripts and Add-Ins**
5. Select the **Add-Ins** tab
6. Find "Buckminster Fusion" in the list and click **Run**

## Usage

1. After installation, find the **Buckminster Fusion** command in the CREATE panel (SOLID tab)
2. Click the command to open the dialog
3. Adjust parameters:
   - **Radius**: The radius of the geodesic sphere
   - **Frequency**: The subdivision frequency (higher = more triangular faces)
4. Click **OK** to generate the geodesic sphere

> ⚠️ **Performance Warning**: Higher frequency values (4+) generate a large number of faces and may cause slow performance or freezing in Fusion 360. Start with lower frequencies (2-3) and increase gradually based on your system's capabilities.

## Technical Details

### Geodesic Sphere Generation

The add-in uses a classic icosahedron subdivision algorithm:

1. Creates a base icosahedron (20-sided polyhedron)
2. Subdivides each triangular face based on the frequency parameter
3. Projects all vertices onto a sphere surface
4. Merges duplicate vertices
5. Generates the final triangulated mesh

### Files

- `BuckminsterFusion.py` - Main add-in script with UI integration
- `lib/geodesic_math.py` - Core geodesic sphere calculation logic
- `BuckminsterFusion.manifest` - Add-in metadata and configuration
- `resources/` - Icon resources for the add-in
  - `16x16.svg` - Small icon (16×16px)
  - `32x32.svg` - Medium icon (32×32px)
  - `fuller_glasses_icon.svg` - Main icon featuring Buckminster Fuller's iconic thick-rimmed glasses

### Algorithm

The geodesic calculation is based on the pyDome approach, adapted for Fusion 360's API. It ensures proper vertex merging to avoid duplicate points and maintains clean topology suitable for 3D modeling and fabrication.

## About Buckminster Fuller and Geodesic Domes

While the geodesic dome concept was first developed in Germany by Walter Bauersfeld for Carl Zeiss and Leica in the 1920s (notably for planetarium construction), R. Buckminster Fuller (1895-1983) was an American architect, systems theorist, and inventor who popularized and extensively developed the geodesic dome structure. His designs demonstrated that spherical structures made of triangular elements are remarkably strong and efficient, using minimal materials to enclose maximum volume. Fuller's work brought geodesic domes into mainstream architecture and engineering.

## Version

Current version: 1.0.0

## Supported Platforms

- Windows
- macOS

## License

This project is open source. See repository for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
