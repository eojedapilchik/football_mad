from typing import Optional

import gspread
from google.oauth2 import service_account
from gspread.utils import InsertDataOption


class GoogleSheetService:
    def __init__(
            self,
            sheet_id: str,
            json_key_filename: str = "footballmad-52be88097f72.json",
    ):
        """
        Initialize the GoogleSheetService.

        :param sheet_id: The ID of the Google Sheet (from the URL)
        :param json_key_filename: Path to the service account JSON credentials
        """
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = service_account.Credentials.from_service_account_file(
            json_key_filename, scopes=scopes
        )
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(sheet_id)

    def append_row(self, values: list, tab_name: Optional[str] = None):
        """
        Append a row to the specified tab in the spreadsheet.

        :param values: A list of values to append as a row
        :param tab_name: The name of the tab (sheet) to append to. Defaults to the first sheet.
        """
        worksheet = self._get_worksheet(tab_name)
        response = worksheet.append_row(
            values, insert_data_option=InsertDataOption.insert_rows
        )
        # if response:
        #     print(f" Response GSHEET {response}")
        # else:
        #     print("❌ Failed to append row.")

    def get_all_rows(self, tab_name: Optional[str] = None) -> list[list[str]]:
        """
        Get all rows from the specified tab in the spreadsheet.

        :param tab_name: The name of the tab (sheet) to read from. Defaults to the first sheet.
        :return: A list of rows, where each row is a list of strings
        """
        worksheet = self._get_worksheet(tab_name)
        return worksheet.get_all_values()

    def _get_worksheet(self, tab_name: Optional[str] = None):
        """
        Helper to get the worksheet by tab name or return the first sheet if none provided.
        """
        if tab_name:
            return self.sheet.worksheet(tab_name)
        return self.sheet.get_worksheet(0)


if __name__ == "__main__":
    # Replace with your actual sheet ID (from the Google Sheets URL)
    sheet_id = "1ogMvKidrN86cMfYe7lii0mEqZ8AWojQ-Fwmm-MBYiQs"
    service = GoogleSheetService(sheet_id)

    # Append a test row to a specific tab
    test_row = ["Hello", "World", 123]
    service.append_row(test_row, tab_name="Sheet2")
    print("✅ Row appended to 'Sheet2'.")

    # Fetch and print all rows from a specific tab
    all_rows = service.get_all_rows(tab_name="Sheet2")
    for row in all_rows:
        print(row)
