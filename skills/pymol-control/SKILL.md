---
name: pymol-control
description: Control PyMOL molecular visualization software through AI. Use when user wants to visualize molecular structures, analyze proteins/DNA/RNA, create publication-quality images, or perform any molecular graphics operations.
---

# PyMOL Control

Control PyMOL molecular visualization software to load structures, create visualizations, and generate publication-quality images.

## Prerequisites

Before using PyMOL tools, ensure:

1. **PyMOL is running with XML-RPC server enabled**:
   ```bash
   pymol -R
   # or
   pymol --rpc-server
   ```

2. **MCP server is configured** in kimi-cli to connect to `pymol_mcp_server.py`

## Common Workflows

### Loading Structures

**From PDB database:**
```
Fetch protein structure 1ABC from PDB
```

**From local file:**
```
Load the PDB file at /path/to/structure.pdb
```

### Basic Visualization

**Show molecular representation:**
```
Show cartoon representation for all atoms
Show sticks for the ligand
Show surface for the protein
```

**Color schemes:**
```
Color by rainbow (N-term to C-term)
Color chain A red, chain B blue
Set background to white
```

### Selection and Analysis

**Create selections:**
```
Select the binding site as "site" around resi 100
Select all water molecules
Select the ligand as "ligand"
```

**Zoom and orient:**
```
Zoom to the binding site
Orient the protein to show the active site
```

### Creating Publication Images

**High-quality rendering:**
```
Set background to white
Ray trace with 2400x2400 resolution
Save as PNG image
```

## Available MCP Tools

### File Operations
- `pymol_load` - Load structure from file
- `pymol_fetch` - Fetch from PDB database
- `pymol_save` - Save structure to file

### Display Control
- `pymol_show` - Show representation (lines, sticks, spheres, surface, mesh, cartoon, ribbon, dots)
- `pymol_hide` - Hide representation

### Color Control
- `pymol_color` - Set object/selection color
- `pymol_bg_color` - Set background color

### View Control
- `pymol_zoom` - Zoom to selection
- `pymol_orient` - Orient to selection
- `pymol_rotate` - Rotate view or object
- `pymol_reset` - Reset view

### Selection
- `pymol_select` - Create named selection
- `pymol_delete` - Delete object/selection

### Information
- `pymol_get_names` - List all objects
- `pymol_count_atoms` - Count atoms in selection
- `pymol_get_pdb` - Get PDB format string

### Rendering
- `pymol_ray` - Ray trace rendering
- `pymol_draw` - OpenGL rendering
- `pymol_png` - Save PNG image

### Advanced
- `pymol_do` - Execute arbitrary PyMOL command

## Selection Expressions

PyMOL uses powerful selection syntax:

| Selection | Description |
|-----------|-------------|
| `all` | All atoms |
| `name CA` | Alpha carbons |
| `resi 1-100` | Residues 1-100 |
| `chain A` | Chain A |
| `resn ALA` | Alanine residues |
| `hetatm` | Heteroatoms (ligands, waters) |
| `organic` | Organic molecules (ligands) |
| `resi 100 around 5` | Atoms within 5Å of residue 100 |
| `byres (resi 100 expand 8)` | Complete residues within 8Å |

## Color Names

Common PyMOL colors: `red`, `green`, `blue`, `yellow`, `magenta`, `cyan`, `orange`, `purple`, `pink`, `gray`, `white`, `black`, `rainbow`, `cpk`, `spectrum`

## Examples

### Example 1: Basic Protein Visualization
```
1. Fetch structure 1AKE (Adenylate Kinase)
2. Show cartoon representation
3. Color by rainbow
4. Set white background
5. Zoom to the protein
```

### Example 2: Ligand Binding Site Analysis
```
1. Load protein structure
2. Select the ligand as "ligand"
3. Select binding site as "site" around ligand within 5Å
4. Show sticks for ligand and site
5. Show surface for the rest
6. Color site residues differently
```

### Example 3: Publication Figure
```
1. Load structure
2. Set white background
3. Show cartoon with rainbow coloring
4. Show sticks for important residues
5. Ray trace at 2400x2400
6. Save high-resolution PNG
```

## Troubleshooting

**Connection issues:**
- Ensure PyMOL was started with `-R` flag
- Check if PyMOL XML-RPC is running on port 9123
- Verify MCP server configuration

**Command not working:**
- Use `pymol_do` for complex PyMOL commands
- Check selection syntax
- Verify object names exist

## References

- PyMOL Documentation: https://pymolwiki.org/
- Selection Algebra: https://pymolwiki.org/index.php/Selection_Algebra
- Color Values: https://pymolwiki.org/index.php/Color
