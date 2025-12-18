import json
from fpdf import FPDF
from datetime import datetime
from typing import Dict
from core.config import OUTPUTS_DIR as PDF_OUTPUT_DIR
import os

# --- Configuration for Dynamic Formatting ---
MAX_PAGE_HEIGHT = 277  # A4 Height (297) - 20mm total margin
FONT_SIZES = [12, 11.5, 11, 10.5, 10]
# LINE_SPACING_LEVELS = [6.0, 5.0, 4.0]  # High, Medium, Tight (line height)
MARGIN_LEVELS = [
    12,
    10,
    8,
    6,
]  # Standard (15mm), Tight (12mm), Narrow (10mm), Very Narrow (6mm)

FONT_PATH = "data/fonts/calibri-font-family"


# --- 1. Date Sorting Helper ---
def get_start_date_object(experience_entry):
    """Converts a date string (e.g., 'Jan 2024' or 'Present') to a sortable object."""
    date_str = experience_entry.get("start_date", "Jan 1900")
    if date_str.lower() == "present":
        return datetime.now()

    try:
        # Tries to parse 'MMM YYYY' format
        return datetime.strptime(date_str.replace("Sept", "Sep"), "%b %Y")
    except ValueError:
        return datetime.min


# --- 2. Dynamic PDF Generator Class ---
class DynamicResumePDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_font_size = 9.5
        self.line_height_factor = 4.5
        self.default_margin = 15
        self.narrow_margin = 10

    def set_adaptive_margins(self, margin):
        self.set_left_margin(margin)
        self.set_right_margin(margin)
        self.w = self.w - 2 * margin
        self.l_margin = margin
        self.r_margin = margin
        self.x = margin

    def set_font_size_and_height(self, size):
        self.base_font_size = size
        self.line_height_factor = size * 0.45
        self.add_font(
            "Calibri", "", os.path.join(FONT_PATH, "calibri-regular.ttf"), uni=True
        )
        self.add_font(
            "Calibri", "B", os.path.join(FONT_PATH, "calibri-bold.ttf"), uni=True
        )
        self.add_font(
            "Calibri", "I", os.path.join(FONT_PATH, "calibri-italic.ttf"), uni=True
        )
        self.add_font(
            "Calibri",
            "BI",
            os.path.join(FONT_PATH, "calibri-bold-italic.ttf"),
            uni=True,
        )

        self.set_font("Calibri", "", size)

    def print_section_title(self, label):
        self.set_text_color(0, 0, 0)  # Ensure Black for Title
        self.set_font("Calibri", "B", self.base_font_size + 1.5)  # type: ignore
        self.cell(0, self.line_height_factor * 1.5, label.upper(), 0, 1, "L")
        self.line(self.l_margin, self.get_y(), self.w + self.l_margin, self.get_y())
        self.ln(self.line_height_factor / 2)

    def print_entry_header(self, title, date, company, location):
        self.set_text_color(0, 0, 0)  # Ensure Black for Header
        # Position Title (Bold) and Date (Bold, Right)
        self.set_font("Calibri", "B", self.base_font_size)  # type: ignore
        self.cell(self.w * 0.75, self.line_height_factor, title, 0, 0, "L")
        self.set_font("Calibri", "B", self.base_font_size - 0.5)  # type: ignore
        self.cell(self.w * 0.25, self.line_height_factor, date, 0, 1, "R")

        # Company (Italic) and Location (Italic, Right)
        self.set_font("Calibri", "I", self.base_font_size)  # type: ignore
        self.cell(self.w * 0.75, self.line_height_factor, company, 0, 0, "L")
        self.set_font("Calibri", "I", self.base_font_size - 0.5)  # type: ignore
        self.cell(self.w * 0.25, self.line_height_factor, location, 0, 1, "R")
        self.ln(1)

    def print_bullet_point(self, text):
        self.set_text_color(0, 0, 0)  # Ensure Black for Bullet Point
        self.set_font("Calibri", "", self.base_font_size)  # type: ignore
        self.set_x(self.l_margin + 3)
        self.multi_cell(0, self.line_height_factor, f"• {text}")
        self.ln(0.5)

    def print_text_content(self, text, style=""):
        self.set_text_color(0, 0, 0)  # Ensure Black for Summary/Plain text
        self.set_font("Calibri", style, self.base_font_size)  # type: ignore
        self.multi_cell(0, self.line_height_factor, text)
        self.ln(self.line_height_factor)


# --- 3. Main Generation Function ---
def generate_pdf_resume(data: Dict, target_role: str) -> str:

    # 3.1. Content Pre-structuring and Sorting (Reverse Chronological)
    exps_list = list(data["experiences"].values())
    exps_list.sort(key=get_start_date_object, reverse=True)

    edus_list = list(data["educations"].values())
    edus_list.sort(key=get_start_date_object, reverse=True)

    skill_groups = []
    for category, items_str in data["skills"].items():
        if type(items_str) is list:
            items = ", ".join(items_str)
        elif type(items_str) is str:
            items = items_str.replace(",", ", ").replace("  ", " ")
        skill_groups.append((category.replace("_", " ").title(), items))

    # 3.2. Define Page Content Block (function for reuse in fitting attempts)
    def render_content(pdf_instance, font_size, margin):
        pdf_instance.set_adaptive_margins(margin)
        pdf_instance.set_font_size_and_height(font_size)
        pdf_instance.set_auto_page_break(auto=True, margin=10)

        # --- HEADER ---
        pdf_instance.set_text_color(0, 0, 0)  # Ensure Black for Name/Contact Info
        pdf_instance.set_font("Calibri", "B", font_size + 10)
        pdf_instance.cell(0, 10, data["name"], 0, 1, "C")

        pdf_instance.set_font("Calibri", "", font_size)
        contact_line_1 = f"{data['phone_number']} | {data['email']} | {data['address']}"
        pdf_instance.cell(0, pdf_instance.line_height_factor, contact_line_1, 0, 1, "C")

        # Links Line (Clickable links)
        links = [
            ("LinkedIn", data["linkedin"]),
            ("GitHub", data["github"]),
            ("Portfolio", data["portfolio_website"]),
        ]

        link_str = " | ".join([name for name, url in links])
        total_width = pdf_instance.get_string_width(link_str)
        start_x = (210 - total_width) / 2 - 3
        pdf_instance.set_x(start_x)

        for i, (name, url) in enumerate(links):
            # Set to BLUE for the hyperlink
            pdf_instance.set_text_color(0, 0, 255)
            pdf_instance.set_font("Calibri", "U", font_size)
            w = pdf_instance.get_string_width(name)
            pdf_instance.cell(
                w, pdf_instance.line_height_factor, name, 0, 0, "C", link=url
            )

            # IMMEDIATELY RESET COLOR TO BLACK
            pdf_instance.set_text_color(0, 0, 0)
            pdf_instance.set_font("Calibri", "", font_size)

            if i < len(links) - 1:
                pdf_instance.cell(3, pdf_instance.line_height_factor, " | ", 0, 0, "C")

        pdf_instance.ln(pdf_instance.line_height_factor * 2)

        # Ensure text color is black before starting any new section
        pdf_instance.set_text_color(0, 0, 0)

        # --- SUMMARY (Optional) ---
        if len(data.get("summary")) > 0:  # type: ignore
            pdf_instance.print_section_title("Professional Summary")
            pdf_instance.print_text_content(data["summary"])

        # --- TECHNICAL SKILLS ---
        pdf_instance.print_section_title("Technical Skills")
        for category, items in skill_groups:
            pdf_instance.set_font("Calibri", "B", font_size)
            pdf_instance.cell(
                pdf_instance.w * 0.25,
                pdf_instance.line_height_factor,
                f"{category}:",
                0,
                0,
            )
            pdf_instance.set_font("Calibri", "", font_size)
            pdf_instance.multi_cell(0, pdf_instance.line_height_factor, items)
        pdf_instance.ln(2)

        # --- PROFESSIONAL EXPERIENCE ---
        pdf_instance.print_section_title("Professional Experience")
        for exp in exps_list:
            date_range = f"{exp['start_date']} - {exp['end_date']}"
            pdf_instance.print_entry_header(
                exp["position"], date_range, exp["company"], exp["location"]
            )
            for desc in exp["description"]:
                pdf_instance.print_bullet_point(desc)
            pdf_instance.ln(1.5)

        # --- KEY PROJECTS ---
        if data.get("projects"):
            pdf_instance.print_section_title("Key Projects")
            for proj in data["projects"].values():
                pdf_instance.set_font("Calibri", "B", font_size)
                pdf_instance.cell(
                    0,
                    pdf_instance.line_height_factor,
                    f"{proj['name']} | {proj['technologies']}",
                    0,
                    1,
                )
                for desc in proj["description"]:
                    pdf_instance.print_bullet_point(desc)
                pdf_instance.ln(1.5)

        # --- EDUCATION ---
        pdf_instance.print_section_title("Education")
        for edu in edus_list:
            date_range = f"{edu['start_date']} - {edu['end_date']}"
            pdf_instance.set_font("Calibri", "B", font_size)
            pdf_instance.cell(
                pdf_instance.w * 0.75,
                pdf_instance.line_height_factor,
                edu["degree"] + " - " + edu["field_of_study"],
                0,
                0,
            )
            pdf_instance.set_font("Calibri", "B", font_size - 0.5)
            pdf_instance.cell(
                pdf_instance.w * 0.25,
                pdf_instance.line_height_factor,
                date_range,
                0,
                1,
                "R",
            )

            pdf_instance.set_font("Calibri", "I", font_size)
            pdf_instance.cell(
                0, pdf_instance.line_height_factor, edu["university"], 0, 1
            )
            pdf_instance.ln(1)

        # --- CERTIFICATIONS & LICENSES ---
        if data.get("certifications"):
            pdf_instance.print_section_title("Certifications & Licenses")
            pdf_instance.set_font("Calibri", "", font_size)
            for cert in data["certifications"].values():
                pdf_instance.cell(
                    0,
                    pdf_instance.line_height_factor,
                    f"• {cert['name']} ({cert['issuer']}) ",
                    0,
                    0,
                )
                pdf_instance.cell(
                    pdf_instance.w * 0.10,
                    pdf_instance.line_height_factor,
                    cert["date"],
                    0,
                    1,
                    "R",
                )

    # 3.3. Dynamic Fitting Logic (Remains the same)
    final_pdf = None

    # Define the dynamic scaling sequence (same as before)
    scaling_options = []
    for margin in MARGIN_LEVELS:
        for font_size in FONT_SIZES:
            scaling_options.append((font_size, margin))

    scaling_options = sorted(list(set(scaling_options)), reverse=True)
    # print(scaling_options)
    # 3. ITERATE THROUGH SCALING OPTIONS TO FIT CONTENT
    for i, (font_size, margin) in enumerate(scaling_options):
        # Attempt 1: Default Font (9.5pt) and Standard Margin (15mm)
        print(f"Attempt {i+1}: Font Size: {font_size}pt, Margin: {margin}mm")
        test_pdf = DynamicResumePDF("P", "mm", "A4")
        test_pdf.add_page()
        render_content(test_pdf, font_size, margin)
        if test_pdf.page_no() == 1:
            final_pdf = test_pdf
            print(
                "✅ Success! Content fits on one page. With settings: Font Size:"
                f" {font_size}pt, Margin: {margin}mm"
            )
            break
    else:
        print("All attempts completed. Content may exceed one page.")
        test_pdf = DynamicResumePDF("P", "mm", "A4")
        test_pdf.add_page()
        render_content(test_pdf, 12.0, 10)
        final_pdf = test_pdf
        print(
            "⚠️ Warning: Content still exceeds one page. Generating multi-page PDF"
            " with font 11pt/ default margin."
        )

    # 5. FINALIZATION
    # os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    safe_name = data.get("name", "Resume").replace(" ", "_")
    safe_role = target_role.replace(" ", "_").replace("/", "").replace("\\", "")
    filename = f"{safe_name}_{safe_role}_Tailored_Resume.pdf"
    output_path = os.path.join(PDF_OUTPUT_DIR, filename)

    final_pdf.output(output_path)

    print(f"✅ PDF successfully generated and saved to: {output_path}")
    return output_path


# --- Example Usage ---
# if __name__ == "__main__":
#     with open("sample_master_background.json", "r") as f:
#         sample_data = json.load(f)
#     generate_pdf_resume(sample_data, "AI/ML Specialist")
