
import re
from datetime import date
from agent import list_invoices, read_invoice, save_invoice, verify_invoice


def parse_invoice(content):
    fields = {}
    for line in content.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def run_offline(task):
    print("\n[1] Planning: find matching invoices")

    match = re.search(
        r"(?:invoice|invoices)\s+from\s+(.+?)(?:,|\.|$)",
        task,
        re.IGNORECASE,
    )
    vendor = match.group(1).strip() if match else None

    if not vendor:
        return "Please specify a vendor, for example: latest invoice from ABC Technologies."

    candidates = []

    print("[2] Listing and reading invoice files")
    for item in list_invoices():
        filename = item["filename"]
        result = read_invoice(filename)

        if "error" in result:
            print(f"    Skipping {filename}: {result['error']}")
            continue

        fields = parse_invoice(result["content"])

        if fields.get("Vendor", "").casefold() != vendor.casefold():
            continue

        try:
            issued = date.fromisoformat(fields["Issue Date"])
        except (KeyError, ValueError):
            print(f"    Skipping {filename}: invalid issue date")
            continue

        candidates.append((issued, filename, fields))

    if not candidates:
        return f"No valid invoices found for {vendor}."

    _, filename, fields = max(candidates, key=lambda item: item[0])
    print(f"[3] Selected latest invoice: {filename}")

    required = [
        "Invoice Number", "Vendor", "Issue Date",
        "Due Date", "Amount", "Currency"
    ]
    missing = [key for key in required if not fields.get(key)]

    if missing:
        return f"Cannot process {filename}: missing {missing}"

    wants_save = bool(re.search(
        r"\b(save|store|record|enter|insert)\b",
        task,
        re.IGNORECASE,
    ))

    if not wants_save:
        return (
            f"Latest invoice: {fields['Invoice Number']}\n"
            f"Vendor: {fields['Vendor']}\n"
            f"Amount: {fields['Currency']} {fields['Amount']}\n"
            f"Due date: {fields['Due Date']}\n"
            f"Source: {filename}\n"
            "No database changes made."
        )

    print("[4] Validating and saving to SQLite")
    result = save_invoice(
        invoice_number=fields["Invoice Number"],
        vendor=fields["Vendor"],
        issue_date=fields["Issue Date"],
        due_date=fields["Due Date"],
        amount=fields["Amount"],
        currency=fields["Currency"],
        source_file=filename,
    )

    if result.get("status") not in ("saved", "already_exists"):
        return f"Save failed: {result}"

    print("[5] Reading database record back for verification")
    check = verify_invoice(fields["Invoice Number"])
    record = check.get("record") or {}

    expected = {
        "invoice_number": fields["Invoice Number"],
        "vendor": fields["Vendor"],
        "issue_date": fields["Issue Date"],
        "due_date": fields["Due Date"],
        "currency": fields["Currency"],
        "source_file": filename,
    }

    verified = (
        check.get("verified") is True
        and all(record.get(k) == v for k, v in expected.items())
    )

    if verified:
        from decimal import Decimal
        verified = Decimal(record["amount"]) == Decimal(fields["Amount"])

    if not verified:
        return "Verification failed: database record does not match source."

    print("[6] Verification successful")
    return (
        f"SUCCESS: Invoice {fields['Invoice Number']} "
        f"({result['status']}).\n"
        f"Vendor: {fields['Vendor']}\n"
        f"Amount: {fields['Currency']} {fields['Amount']}\n"
        f"Due date: {fields['Due Date']}\n"
        f"Source: {filename}\n"
        "Database record independently verified."
    )


if __name__ == "__main__":
    print("Offline Invoice Task Worker (type exit to quit)")

    while True:
        task = input("\nTask> ").strip()

        if task.lower() in ("exit", "quit"):
            break

        if task:
            try:
                print("\n" + run_offline(task))
            except Exception as exc:
                print(f"Error: {type(exc).__name__}: {exc}")
