import io
from typing import List, Tuple, Dict
import pandas as pd
from pydantic import ValidationError

from app.schemas.common_prospect import CommonProspectInput, ExcelIntakeRow


def parse_excel_upload(file_contents: bytes, filename: str) -> Tuple[List[CommonProspectInput], List[Dict]]:
    """
    Parses an uploaded Excel (.xlsx) or CSV file.
    Returns a tuple of (valid_prospects, errors).
    """
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_contents))
    else:
        df = pd.read_excel(io.BytesIO(file_contents))

    # Standardize column names (lowercase, strip whitespace, replace spaces with underscores)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Replace nan with None
    df = df.where(pd.notnull(df), None)

    # Column mapping aliases
    col_mapping = {
        "company": "company_name",
        "name": "contact_name",
        "email": "contact_email",
        "title": "contact_title",
        "phone": "contact_phone",
        "website": "website_url",
        "url": "website_url",
    }
    df.rename(columns=col_mapping, inplace=True)

    valid_prospects = []
    errors = []

    for index, row in df.iterrows():
        row_dict = row.to_dict()
        
        # Ensure minimum required fields exist in dict to avoid KeyError before Pydantic
        if "company_name" not in row_dict or not row_dict["company_name"]:
            errors.append({"row": index + 2, "error": "Missing company_name"})
            continue
        if "website_url" not in row_dict or not row_dict["website_url"]:
            errors.append({"row": index + 2, "error": "Missing website_url"})
            continue
            
        try:
            intake_row = ExcelIntakeRow(**row_dict)
            valid_prospects.append(intake_row.to_common_input())
        except ValidationError as e:
            errors.append({"row": index + 2, "error": str(e)})

    return valid_prospects, errors
