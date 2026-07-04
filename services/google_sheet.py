import gspread


class GoogleSheetService:


    def __init__(
        self,
        credentials
    ):
        self.client = (
            gspread.service_account(
                filename=credentials
            )
        )


    def open_sheet(
        self,
        name
    ):
        return self.client.open(name)


    def read_tab(
        self,
        sheet_name,
        tab
    ):
        sheet = self.open_sheet(sheet_name)

        return (
            sheet
            .worksheet(tab)
            .get_all_records()
        )


    def write_rows(
        self,
        sheet_name,
        tab,
        rows
    ):

        sheet = (
            self
            .open_sheet(sheet_name)
        )

        worksheet = (
            sheet
            .worksheet(tab)
        )

        worksheet.append_rows(rows)