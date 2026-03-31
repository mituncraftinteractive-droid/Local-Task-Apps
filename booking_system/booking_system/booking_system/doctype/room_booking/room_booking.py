import frappe
from frappe.model.document import Document
import qrcode
from io import BytesIO


class RoomBooking(Document):

    def validate(self):
        self.check_department()
        self.check_conflict()

    def on_submit(self):
        frappe.log_error(message=f"on_submit called for {self.name}", title="QR Debug")
        self.generate_qr_code()

    # -------------------------
    # Department restriction
    # -------------------------
    def check_department(self):
        user_dept = frappe.db.get_value(
            "Employee",
            {"user_id": frappe.session.user},
            "department"
        )

        if user_dept and self.department != user_dept:
            frappe.throw("You can only book rooms for your own department.")

    # -------------------------
    # Conflict detection
    # -------------------------
    def check_conflict(self):
        conflict = frappe.db.sql("""
            SELECT name FROM `tabRoom Booking`
            WHERE meeting_room = %s
            AND name != %s
            AND docstatus < 2
            AND (
                (%s BETWEEN from_time AND to_time)
                OR (%s BETWEEN from_time AND to_time)
                OR (from_time BETWEEN %s AND %s)
            )
        """, (
            self.meeting_room,
            self.name or "",
            self.from_time,
            self.to_time,
            self.from_time,
            self.to_time,  
        ))

        if conflict:
            frappe.throw("This room is already booked for the selected time.")

    # -------------------------
    # QR Code generation
    # -------------------------
    def generate_qr_code(self):
        frappe.log_error(message=f"generate_qr_code called for {self.name}", title="QR Debug")
        print(f"[DEBUG] generate_qr_code called for booking: {self.name}")

        # Step 1: Create QR URL
        qr_data = f"{frappe.utils.get_url()}/api/method/booking_system.api.check_in?booking={self.name}"
        print(f"[DEBUG] QR URL: {qr_data}")

        # Step 2: Generate QR image
        try:
            import qrcode
            from io import BytesIO

            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            print(f"[DEBUG] QR image generated, size: {len(buffer.getvalue())} bytes")

        except Exception as e:
            print(f"[ERROR] QR generation failed: {e}")
            return

        # Step 3: Save as File in ERPNext
        try:
            file = frappe.get_doc({
                "doctype": "File",
                "file_name": f"{self.name}_qr.png",
                "is_private": 0,
                "content": buffer.getvalue(),
                "attached_to_doctype": "Room Booking",
                "attached_to_name": self.name
            })
            file.insert(ignore_permissions=True)
            print(f"[DEBUG] File inserted: {file.file_name}, URL: {file.file_url}")

            # Step 4: Save file URL in Room Booking
            self.db_set("qr_code", file.file_url)
            print(f"[DEBUG] QR code URL saved in Room Booking: {self.name}")

        except Exception as e:
            print(f"[ERROR] File saving failed: {e}")

