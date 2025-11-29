# Starving Artist Gallery

A beautiful web viewer for browsing AI-generated artworks.

## Quick Start

1. **Generate the data**:
   ```bash
   python generate_viewer_data.py
   ```

2. **Start a local server**:
   ```bash
   python3 -m http.server 8000
   ```

3. **Open in browser**:
   ```
   http://localhost:8000/viewer.html
   ```

## Why do I need a server?

Modern browsers block `fetch()` requests when opening HTML files directly (`file://` protocol) for security reasons. Running a simple HTTP server solves this.

## Features

- **Artist Selection**: Switch between different AI artists
- **Timeline View**: See all works chronologically  
- **Full Details**: Click any artwork to view with critique
- **Text & Visual**: Displays both poetry and SVG art
- **Beautiful UI**: Dark, modern design with gradients
