from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_pdf(filename: str = "company_policy.pdf") -> None:
    c = canvas.Canvas(filename, pagesize=letter)

    # --- Page 1: Working Hours & Leaves ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "DocuPulse Technologies - Employee Handbook (Page 1)")

    c.setFont("Helvetica", 11)
    text_p1 = [
        "1. Working Hours & Flexibility:",
        "Standard working hours are Monday through Friday, 09:00 to 18:00.",
        "Fridays are designated as 'Focus Days' and work hours end early at 16:30.",
        "A hybrid model is in effect, permitting employees to work remotely 2 days per week.",
        "",
        "2. Annual Leave Policy:",
        "Employees completing 1 full year of tenure are granted 18 business days of paid annual leave.",
        "For employees with more than 5 years of tenure, annual leave increases to 24 business days.",
        "Unused leave days must be transferred or utilized before the end of Q1 (March 31st).",
        "",
        "3. Learning & Development Budget:",
        "Each software engineer receives an annual personal budget of $1,500 for courses and conferences."
    ]

    y = 700
    for line in text_p1:
        c.drawString(50, y, line)
        y -= 22

    c.showPage()

    # --- Page 2: IT Security & Equipment ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "DocuPulse Technologies - Information Security (Page 2)")

    c.setFont("Helvetica", 11)
    text_p2 = [
        "4. Hardware & Equipment Provisioning:",
        "All engineers receive a 32GB RAM Apple MacBook Pro or Lenovo ThinkPad upon joining.",
        "Hardware issues must be submitted to the IT Helpdesk via Slack on #it-support.",
        "The standard hardware refresh cycle is strictly set to 36 months (3 years).",
        "",
        "5. Data Security & Credential Governance:",
        "Two-factor authentication (2FA) is mandatory across all corporate accounts.",
        "Passwords must be at least 12 characters long and rotated every 90 days.",
        "Production database credentials must never be shared in direct Slack channels.",
        "Violations of confidentiality agreements will result in immediate termination."
    ]

    y = 700
    for line in text_p2:
        c.drawString(50, y, line)
        y -= 22

    c.save()
    print(f"File '{filename}' generated successfully!")

if __name__ == "__main__":
    create_sample_pdf()