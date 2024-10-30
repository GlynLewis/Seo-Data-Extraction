# SEO Data Extraction Tool

## Project Overview
The SEO Data Extraction Tool is a powerful application designed to automate the process of gathering SEO-related data for WordPress websites. It provides valuable insights into domain ranking, backlink profiles, indexed pages, and more.

## Features
- CSV input for bulk website processing
- Detection of WordPress sites
- Extraction of domain rank, backlink data, and contact information
- Sitemap parsing for total page count
- Google indexed pages estimation
- User-friendly GUI built with PyQt6
- Cross-platform compatibility (Windows and macOS)

## Installation

No installation is required. The SEO Data Extraction Tool is provided as a standalone application for both Windows and macOS.

### For Windows Users:
1. Download the `SEODataExtraction.exe` file from the latest release.
2. Double-click the executable to run the application.


## Usage
1. Launch the application by double-clicking the executable (.exe for Windows)
2. In the application window, click "Upload CSV" to select your input file containing website URLs.
3. Click "Process WordPress Sites" to start the data extraction process.
4. Once processing is complete, use the "Export Results" button to save the extracted data as a CSV file.

### Input CSV Format
Ensure your input CSV file has the following columns:
- first_name
- last_name
- email
- organization_name
- title
- website_url
- phone_number

The tool will primarily use the 'website_url' column for data extraction.