import csv


def export_logs(
    rows,
    file_path
):

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "id",
            "group_id",
            "user_id",
            "action",
            "created_at"
        ])

        writer.writerows(rows)