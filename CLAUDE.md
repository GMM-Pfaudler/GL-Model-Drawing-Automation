# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Autodesk Inventor 3D model automation system** for GMM Pfaudler's Glass Lined Technology division. It automates the generation of reactor 3D CAD models from configuration parameters.

## Architecture

**Three-application monorepo:**

```
gl-reactor/          # Vue.js + Quasar SPA (Frontend)
gl-reactor-rest/     # Python FastAPI (Backend API + Inventor automation)
gl-vault-api/        # .NET Core 8.0 (Autodesk Vault integration)
```

**Data Flow:**
1. Frontend collects reactor configuration via component forms
2. FastAPI backend orchestrates model generation
3. Vault API retrieves component files from Autodesk Vault
4. InventorService uses COM automation to generate 3D models

**Databases:**
- MySQL: OFN (Order Form Number) specifications
- MongoDB: Configuration storage
- Excel files: Component data persisted to `D:\GL\` directory structure

## Development Commands

### Frontend (gl-reactor)
```bash
cd gl-reactor
npm install          # Install dependencies
npm run dev          # Start dev server with hot reload
npm run build        # Build for production (outputs to dist/)
npm run lint         # ESLint validation
npm run format       # Prettier formatting
```

### Backend (gl-reactor-rest)
```bash
cd gl-reactor-rest
python -m venv glenv              # Create virtual environment
glenv\Scripts\activate            # Activate (Windows)
pip install -r requirements.txt   # Install dependencies
fastapi dev main.py               # Run with auto-reload
python main.py                    # Run in debug mode (port 8000)
```

### Vault API (gl-vault-api)
```bash
cd gl-vault-api/VaultWebApplication
dotnet build         # Build project
dotnet run           # Run (port 5157)
```

## Key API Endpoints (FastAPI)

All endpoints prefixed with `/api/v1`:

| Endpoint | Purpose |
|----------|---------|
| `POST /getofn` | Fetch OFN specification by SFON number |
| `POST /getmasters` | Get master data (jacket, pressure, temperature) |
| `POST /save` | Save component data to Excel |
| `POST /search` | Search component by item code |
| `POST /savetojson` | Save component details to JSON |
| `POST /save-component-progress` | Save component with unique ID tracking |
| `POST /generate` | Generate 3D model via Inventor |
| `POST /open` | Open generated component in Inventor |

## Backend Service Layer

```
services/
├── ofn_service.py           # OFN database operations
├── vault_service.py         # Vault file retrieval (base64 encoding)
├── inventor_service.py      # Inventor COM API interaction
├── generation_service.py    # Model generation orchestration
├── component_service.py     # Excel component save/search
├── mongo_service.py         # MongoDB operations
```

## Frontend Component Structure

Each reactor component has its own Vue component form in `gl-reactor/src/components/`:
- Core: Monoblock, Jacket, Insulation, Drive Assembly
- Accessories: Agitator, Gearbox, Motor, Drive Hood
- Sealing: Shaft Closure, Mechanical Seal, COC
- Structural: Manhole Cover, Diaphragm Ring, Body Flange C-Clamp

The main layout (`MainLayout.vue`) contains the toolbar and page container for all component forms.

## Inventor Integration

The backend uses `win32com.client` for COM automation with Autodesk Inventor:
- Supports `.ipt` (part) and `.iam` (assembly) files
- `pywinauto` for window automation
- Files retrieved from Vault are base64 encoded/decoded

## Environment Configuration

The `.env` file contains:
- MySQL credentials (HOST, USER, PASSWORD)
- MongoDB URI

Vault connection uses hardcoded credentials to server `172.30.0.14`.

## Windows-Only Requirement

This application requires Windows due to:
- Autodesk Inventor COM automation (`win32com`, `pywinauto`)
- .NET Vault API with Autodesk SDK DLLs

## Recent Optimizations

### inventor_service.py (January 2026)
The Inventor COM automation service was optimized with:
- **Constants extraction**: Constraint codes, nozzle angles, plane names
- **Helper methods**: `_get_geometry_proxies`, `_add_mate_constraint`, `_add_flush_constraint`, `_create_angled_plane`, `_create_circular_pattern`
- **COM lifecycle management**: Context manager support (`with Inventor() as inv:`)
- **Improved error handling**: Proper logging instead of print/bare except
- **Degree-based geometry lookup**: New methods for dynamic plane/axis identification:
  - `get_work_plane_by_degree(work_planes, target_degree, tolerance)`: Finds a WorkPlane by calculating its normal vector's angle in the XZ plane (around Y-axis) using `WorkPlane.Plane.Normal`
  - `get_work_axis_by_degree(work_axes, target_degree, tolerance)`: Finds a WorkAxis by calculating its direction vector's angle in the XZ plane using `WorkAxis.Line.Direction`

See `gl-reactor-rest/INVENTOR_SERVICE_OPTIMIZATION.md` for full details.

### ofn_db.py Security Fix
SQL injection vulnerabilities were fixed by parameterizing all queries and adding table name whitelist validation.

See `gl-reactor-rest/BACKEND_ANALYSIS.md` for security analysis.
