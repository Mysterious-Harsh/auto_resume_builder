from typing import List, Dict
from core.data_models import FilteredResumeContent, FilteredBulletPoint


def organize_resume_content(
    master_background: Dict, filtered_content: FilteredResumeContent
) -> Dict:
    Organized_resume_data = master_background.copy()
    # C. DYNAMIC CONTENT SECTIONS (Group content once)

    content_map: Dict[str, Dict[str, List[str]]] = {}
    for item in filtered_content.bullet_points:
        type = item.metadata.type
        source_id = item.metadata.source_id
        if type not in content_map:
            content_map[type] = {}
        if source_id not in content_map[type]:
            content_map[type][source_id] = []
        content_map[type][source_id] += [item.bullet_point]
    # print(content_map)
    print("Content Map:", content_map.get("skills"))
    print("Content Map:", content_map.get("experiences"))
    print("Content Map:", content_map.get("projects"))
    print("Content Map:", content_map.get("certifications"))

    print("\n--- Organizing Filtered Content into Resume Structure ---")
    print("Replacing SKILLS section...")
    Organized_resume_data["skills"] = content_map.get("skills", {})

    print("Replacing EXPERIENCES section...")
    exp_to_remove = []
    for exp_key in Organized_resume_data.get("experiences", {}):
        if exp_key in content_map.get("experiences", {}):
            Organized_resume_data["experiences"][exp_key]["description"] = content_map[
                "experiences"
            ][exp_key]
        else:
            exp_to_remove.append(exp_key)

    for exp_key in exp_to_remove:
        print(f"Removing experience {exp_key} as experience does not match...")
        del Organized_resume_data["experiences"][exp_key]

    print("Replacing PROJECTS section...")
    proj_to_remove = []
    for proj_key in Organized_resume_data.get("projects", {}):
        if proj_key in content_map.get("projects", {}):
            Organized_resume_data["projects"][proj_key]["description"] = content_map[
                "projects"
            ][proj_key]
        else:
            proj_to_remove.append(proj_key)
    for proj_key in proj_to_remove:
        print(f"Removing project {proj_key} as project does not match...")
        del Organized_resume_data["projects"][proj_key]

    print("Replacing CERTIFICATIONS section...")
    cert_to_remove = []
    for cert_key in Organized_resume_data.get("certifications", {}):
        if cert_key not in content_map.get("certifications", {}):
            cert_to_remove.append(cert_key)
    for cert_key in cert_to_remove:
        print(f"Removing certification {cert_key} as certification does not match...")
        del Organized_resume_data["certifications"][cert_key]

    return Organized_resume_data
