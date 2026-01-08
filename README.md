# Calibration Self Assessment Tool

A portable toolkit for generating annual calibration self-assessments with automated calendar and stakeholder analysis.

## Overview

This project provides Python scripts to analyze calendar data, generate stakeholder insights, and create comprehensive calibration self-assessment materials. The toolkit is designed to be reusable across fiscal years.

## GitHub Pages

The interactive review dashboard is available at:
**https://dfmore.github.io/FY26_Calibration_Self_Assessment_Daniel_Moreira/**

### Setup Notes
- `index.html` at project root is for GitHub Pages deployment
- Original source is maintained in `FY26/deliverables/index.html`
- Images (`social-preview.png`, `kcss.png`) are duplicated at root for GitHub Pages
- GitHub Pages serves from the repository root on the `master` branch

### Local Testing
```bash
python start_server.py
# Opens at http://localhost:8080/
```

## Project Structure

```
Calibration/
├── scripts/              # Reusable Python analysis tools
├── docs/                 # Implementation guides and references
├── reference/            # Shared reference materials (e.g., ORBIT guide)
└── FY26/                 # Year-specific data and outputs
    ├── inputs/           # Raw data (calendar, notes, KPIs)
    ├── analysis_outputs/ # Generated analysis files
    └── deliverables/     # Final assessment documents
```

## Quick Start

### For a New Fiscal Year

1. **Copy the FY26 folder structure** as a template for your new year (e.g., FY27)
2. **Place your input files** in `FY27/inputs/`:
   - Calendar export (.ics file)
   - Personal notes and achievements
   - KPIs and goals
3. **Run the analysis scripts** from the `scripts/` folder
4. **Review outputs** in `FY27/analysis_outputs/`
5. **Create deliverables** in `FY27/deliverables/`

### Available Scripts

Located in `scripts/`:

- **`analyze_calendar.py`** - Basic calendar event analysis
- **`rerun_analysis_improved.py`** - Enhanced calendar analysis (meetings only)
- **`stakeholder_analysis.py`** - Stakeholder interaction analysis
- **`analyze_by_tags.py`** - Tag-based event categorization
- **`investigate_uncategorized.py`** - Debug uncategorized events
- **`query_calendar.py`** - Interactive calendar queries
- **`generate_calibration_summary.py`** - Generate summary documents

## Usage Instructions

### Running Calendar Analysis

```bash
# From project root
python scripts/rerun_analysis_improved.py
```

The script will:
1. Look for calendar file in current year's `inputs/` folder
2. Generate analysis outputs in `analysis_outputs/` folder
3. Create JSON and text reports

### Running Stakeholder Analysis

```bash
python scripts/stakeholder_analysis.py
```

Analyzes meeting patterns to identify key stakeholders and collaboration metrics.

### Customization

Edit the scripts to customize:
- Event categorization rules
- Stakeholder identification logic
- Output formats
- Analysis metrics

## Documentation

See `docs/` folder for:
- **CALIBRATION_REFERENCE.md** - Complete analysis reference
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details

## Reference Materials

The `reference/` folder contains shared materials like the Autodesk ORBIT Culture Guide that apply across all years.

## Current Years

- **FY26** - Complete (see FY26/deliverables/)

## Requirements

- Python 3.x
- icalendar library (`pip install icalendar`)
- Standard library modules (json, datetime, collections)

## Notes

- All personal data stays in year-specific folders
- Scripts are year-agnostic and portable
- Output formats are consistent across years for easy comparison
