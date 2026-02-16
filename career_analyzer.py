from datetime import datetime
import re


# ---------------- SAFE DATE PARSER ----------------
def parse_date(date_str):
    """
    Try multiple date formats safely.
    """
    for fmt in ("%b %Y", "%B %Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


# ---------------- EXTRACT EXPERIENCE ----------------
def parse_experience_dates(resume_text):

    date_pattern = r"([A-Za-z]{3,9}\s\d{4})\s*[-–]\s*(Present|[A-Za-z]{3,9}\s\d{4})"
    matches = re.findall(date_pattern, resume_text)

    experience_list = []

    for start, end in matches:

        start_date = parse_date(start)

        if end.lower() == "present":
            end_date = datetime.today()
        else:
            end_date = parse_date(end)

        if start_date and end_date:
            experience_list.append((start_date, end_date))

    experience_list.sort(key=lambda x: x[0])

    return experience_list


# ---------------- CAREER GAP DETECTION ----------------
def detect_career_gap(experience_list, gap_threshold=6):

    gaps = []

    for i in range(len(experience_list) - 1):
        end_current = experience_list[i][1]
        start_next = experience_list[i + 1][0]

        gap_months = (start_next.year - end_current.year) * 12 + \
                     (start_next.month - end_current.month)

        if gap_months > gap_threshold:
            gaps.append(gap_months)

    return gaps


# ---------------- JOB HOPPING DETECTION ----------------
def detect_job_hopping(experience_list):

    durations = []

    for start, end in experience_list:
        months = (end.year - start.year) * 12 + \
                 (end.month - start.month)
        durations.append(months)

    if len(durations) == 0:
        return False, 0

    avg_tenure = sum(durations) / len(durations)

    if avg_tenure < 12:
        return True, avg_tenure
    else:
        return False, avg_tenure
