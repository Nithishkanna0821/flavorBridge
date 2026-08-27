import sqlite3
import pandas as pd
import os

def export_users():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '..', 'database', 'database.db')
    export_xlsx = os.path.join(base_dir, '..', 'database', 'registered_users.xlsx')
    export_csv = os.path.join(base_dir, '..', 'database', 'registered_users.csv')

    conn = sqlite3.connect(db_path)
    query = """
        SELECT 
            u.id AS [User ID],
            u.name AS [Full Name],
            u.email AS [Email Address],
            u.role AS [Role],
            u.phone AS [Phone Number],
            u.city AS [City],
            u.address AS [Address],
            u.password_hash AS [Password (Encrypted Hash)],
            u.created_at AS [Registration Date],
            fm.speciality AS [Maker Speciality],
            fm.verification_status AS [Maker Verification Status],
            fm.verification_score AS [Verification Score]
        FROM users u
        LEFT JOIN food_makers fm ON u.id = fm.user_id
        ORDER BY u.id ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Save to Excel & CSV
    df.to_excel(export_xlsx, index=False)
    df.to_csv(export_csv, index=False)
    
    print(f"Export completed successfully!")
    print(f" -> Excel file: {export_xlsx}")
    print(f" -> CSV file:   {export_csv}")

if __name__ == '__main__':
    export_users()
