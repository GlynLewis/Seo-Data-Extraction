import pandas as pd
import csv
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_domain(url):
    """Remove protocol from domain"""
    if isinstance(url, str):
        if url.startswith(('http://', 'https://')):
            url = url.split('://', 1)[1]
    return url

def read_csv(file_path):
    try:
        logger.info(f"Attempting to read CSV file: {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Successfully read CSV with columns: {df.columns.tolist()}")
        
        # Define column mappings (old_name: new_name)
        column_mappings = {
            'firstName': 'first_name',
            'lastName': 'last_name',
            'email': 'email',
            'companyName': 'organization_name',
            'title': 'title',
            'website': 'website_url',
            'phoneNumbers': 'phone_number',
            'linkedIn': 'linkedin_url'
        }
        
        # Log original column names
        logger.info("Original columns before mapping:")
        for col in df.columns:
            logger.info(f"  - {col}")
        
        # Rename columns based on mappings
        for old_name, new_name in column_mappings.items():
            if old_name in df.columns:
                logger.info(f"Mapping column {old_name} to {new_name}")
                df = df.rename(columns={old_name: new_name})
        
        # Log mapped column names
        logger.info("Columns after mapping:")
        for col in df.columns:
            logger.info(f"  - {col}")
        
        required_fields = [
            'first_name', 'last_name', 'email', 'organization_name', 'title',
            'website_url', 'phone_number', 'linkedin_url'
        ]
        
        # Check if all required fields are present in the CSV
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            logger.error(f"Missing required fields in CSV: {', '.join(missing_fields)}")
            logger.error("Available fields: " + ", ".join(df.columns))
            return None
        
        # Ensure we're using the correct column for email
        if 'email' not in df.columns and 'personal_email' in df.columns:
            logger.info("Using 'personal_email' as 'email'")
            df['email'] = df['personal_email']
        
        # Clean website URLs to remove protocols
        if 'website_url' in df.columns:
            logger.info("Cleaning website URLs to remove protocols")
            df['website_url'] = df['website_url'].apply(clean_domain)
        
        # Select only the required fields
        df = df[required_fields]
        
        # Log the number of rows
        logger.info(f"Found {len(df)} rows in CSV")
        
        # Convert DataFrame to list of dictionaries for compatibility with existing code
        records = df.to_dict('records')
        logger.info(f"Converted {len(records)} rows to records format")
        
        # Log a sample of the data
        if records:
            logger.info("Sample of first record:")
            for key, value in records[0].items():
                logger.info(f"  {key}: {value}")

        return records

    except Exception as e:
        logger.error(f"Error reading CSV: {str(e)}")
        return None

def write_csv(data, output_path):
    try:
        logger.error(f"Attempting to write CSV files based on: {output_path}")

        # Convert data to DataFrame if it's a list of dictionaries
        if isinstance(data, list):
            logger.info("Converting list of dictionaries to DataFrame")
            df = pd.DataFrame(data)
        else:
            logger.info("Using provided DataFrame")
            df = data

        logger.info(f"Total records before splitting: {df.shape[0]}")
        logger.info(f"Available columns: {df.columns.tolist()}")

        # Clean website URLs before writing
        if 'website_url' in df.columns:
            logger.info("Cleaning website URLs before writing")
            df['website_url'] = df['website_url'].apply(clean_domain)

        # Get base path and extension
        base_path, ext = os.path.splitext(output_path)
        if not ext:
            ext = '.csv'

        # Check for CMS column (case-insensitive)
        cms_column = None
        for col in df.columns:
            if col.lower() == 'cms':
                cms_column = col
                break

        if cms_column:
            logger.info(f"Found CMS column: {cms_column}")
            # Get unique CMS types
            cms_types = df[cms_column].unique()
            logger.info(f"Found CMS types: {cms_types}")

            # Create a file for each CMS type
            for cms_type in cms_types:
                try:
                    # Handle None/NaN values
                    if pd.isna(cms_type):
                        safe_cms = 'unknown'
                    else:
                        # Create safe filename
                        safe_cms = str(cms_type).lower().replace(' ', '_')
                    
                    if cms_type == 'Error':
                        output_file = f"{base_path}_out_errors{ext}"
                    else:
                        output_file = f"{base_path}_out_{safe_cms}{ext}"
                    
                    # Filter data for this CMS type
                    if pd.isna(cms_type):
                        cms_df = df[df[cms_column].isna()]
                    else:
                        cms_df = df[df[cms_column] == cms_type]
                    
                    # Write to file
                    cms_df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
                    logger.info(f"Wrote {len(cms_df)} rows to {output_file} for CMS type: {cms_type}")
                except Exception as e:
                    logger.error(f"Error writing file for CMS type {cms_type}: {str(e)}")
                    continue
        else:
            logger.info("No 'cms' column found in data, writing all records to single file")
            output_file = f"{base_path}_out_all{ext}"
            df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
            logger.error(f"Wrote {len(df)} rows to {output_file}")

        return True
    except Exception as e:
        logger.error(f"Error writing CSV: {str(e)}")
        return False
