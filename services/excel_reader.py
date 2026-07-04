import pandas as pd

from models.sheet import (
    InfoCriteria,
    TALCompany,
    ResearchInput
)


# Accepted column name aliases (lowercase) → standard name
INFO_COLUMN_MAP = {
    "country":                  "Country",
    "countries":                "Country",
    "industry":                 "Industry",
    "industries":               "Industry",
    "job title":                "Job Title",
    "job titles":               "Job Title",
    "jobtitle":                 "Job Title",
    "title":                    "Job Title",
    "employee size":            "Employee Size",
    "employee_size":            "Employee Size",
    "employees":                "Employee Size",
    "company size":             "Employee Size",
    "max contacts":             "Max Contacts",
    "max_contacts":             "Max Contacts",
    "max contacts per domain":  "Max Contacts",
    "contacts":                 "Max Contacts",
}

TAL_COLUMN_MAP = {
    "company":          "Company",
    "company name":     "Company",
    "company_name":     "Company",
    "organization":     "Company",
    "name":             "Company",
    "domain":           "Domain",
    "website":          "Domain",
    "domain name":      "Domain",
    "url":              "Domain",
}


def _normalize_columns(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """Rename columns using alias map; raise a clear error for anything missing."""
    df.columns = df.columns.str.strip()
    rename = {}
    for col in df.columns:
        standard = column_map.get(col.lower().strip())
        if standard:
            rename[col] = standard
    df = df.rename(columns=rename)
    return df


def _require(df: pd.DataFrame, column: str, sheet: str):
    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' not found in sheet '{sheet}'.\n"
            f"Available columns: {list(df.columns)}\n"
            f"Rename your column to '{column}' or one of its accepted aliases."
        )


class ExcelReader:

    def read(self, file_path: str) -> ResearchInput:
        """
        Read Excel and convert into ResearchInput model.

        Expected sheets:
          - 'Info' : Country | Industry | Job Title | Employee Size | Max Contacts
          - 'TAL'  : Company | Domain
        """

        info_df = pd.read_excel(file_path, sheet_name="Info", engine="openpyxl")
        tal_df  = pd.read_excel(file_path, sheet_name="TAL",  engine="openpyxl")

        info_df = _normalize_columns(info_df, INFO_COLUMN_MAP)
        tal_df  = _normalize_columns(tal_df,  TAL_COLUMN_MAP)

        # Validate required columns exist
        for col in ["Country", "Industry", "Job Title", "Employee Size", "Max Contacts"]:
            _require(info_df, col, "Info")

        for col in ["Company", "Domain"]:
            _require(tal_df, col, "TAL")

        info = InfoCriteria(
            countries=self._split(info_df, "Country"),
            industries=self._split(info_df, "Industry"),
            job_titles=self._split(info_df, "Job Title"),
            employee_size=str(info_df["Employee Size"].iloc[0]).strip(),
            max_contacts_per_domain=int(
                float(info_df["Max Contacts"].iloc[0])
            )
        )

        companies = []

        for _, row in tal_df.iterrows():

            company_name = str(row["Company"]).strip()
            domain       = str(row["Domain"]).strip()

            if company_name and company_name.lower() != "nan":
                companies.append(
                    TALCompany(
                        company_name=company_name,
                        domain=domain if domain.lower() != "nan" else ""
                    )
                )

        return ResearchInput(
            info=info,
            companies=companies
        )


    def _split(self, df: pd.DataFrame, column: str):
        value = str(df[column].iloc[0]).strip()
        return [item.strip() for item in value.split(",") if item.strip()]
