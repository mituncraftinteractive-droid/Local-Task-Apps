import frappe

@frappe.whitelist(allow_guest=True)
def check_in(booking):
    # Get current status
    status = frappe.db.get_value("Room Booking", booking, "check_in_status")
    if status == "Checked In":
        return "Already Checked In"

    # Update check-in status directly
    frappe.db.set_value("Room Booking", booking, "check_in_status", "Checked In")
    frappe.db.commit()

    # Optional: send email if field exists
    organizer_email = frappe.db.get_value("Room Booking", booking, "organizer")
    if organizer_email:
        frappe.sendmail(
            recipients=organizer_email,
            subject="Room Checked In",
            message=f"Your room booking {booking} has been checked in."
        )

    return "Check-In Successful"
