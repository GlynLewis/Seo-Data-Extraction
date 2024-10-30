import pandas as pd
import csv

def read_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        required_fields = [
            'first_name', 'last_name', 'email', 'organization_name', 'title',
            'website_url', 'phone_number', 'linkedin_url'
        ]
        
        # Check if all required fields are present in the CSV
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            print(f"Missing required fields in CSV: {', '.join(missing_fields)}")
            return None
        
        # Ensure we're using the correct column for email
        if 'email' not in df.columns and 'personal_email' in df.columns:
            df['email'] = df['personal_email']
        
        # Select only the required fields
        df = df[required_fields]
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        return data

    except Exception as e:
        print(f"An error occurred while reading the CSV: {str(e)}")
        return None

# def write_csv(data, output_path):
#     try:
#         df = pd.DataFrame(data)

#         # Write to CSV
#         df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
#         print(f"Results written to {output_path}")
#         return True
#     except Exception as e:
#         print(f"An error occurred while writing the CSV: {str(e)}")
#         return False

def write_csv(data, output_path):
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Filter only rows where cms_type is 'WordPress'
        if 'cms_type' in df.columns:
            df = df[df['cms_type'] == 'WordPress']
        
        # Write filtered data to CSV
        df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
        print(f"Results written to {output_path} with {len(df)} WordPress rows.")
        return True
    except Exception as e:
        print(f"An error occurred while writing the CSV: {str(e)}")
        return False
