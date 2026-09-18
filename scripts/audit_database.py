import sqlite3
import json
from pathlib import Path

def audit():
    db_path = Path("data/scholarlens.db")
    if not db_path.exists():
        print(f"Error: {db_path} does not exist.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM scholarships")
    total_count = cursor.fetchone()[0]

    # Synthetic check: how are synthetic records marked in DB or repositories?
    # Let's inspect fingerprint or other markers
    cursor.execute("SELECT count(*) FROM scholarships WHERE fingerprint LIKE 'synth_%' OR name LIKE '%Synthetic%'")
    synth_count = cursor.fetchone()[0]

    cursor.execute("SELECT data_quality, count(*) FROM scholarships GROUP BY data_quality")
    dq_counts = dict(cursor.fetchall())

    cursor.execute("SELECT status, count(*) FROM scholarships GROUP BY status")
    status_counts = dict(cursor.fetchall())

    cursor.execute("SELECT count(DISTINCT name) FROM scholarships")
    distinct_names = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarships WHERE description IS NULL OR trim(description) = ''")
    missing_desc = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarships WHERE provider IS NULL OR trim(provider) = ''")
    missing_prov = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarships WHERE requirements IS NULL OR requirements = '[]' OR requirements = '{}'")
    missing_req = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarships WHERE eligibility_evidence IS NULL")
    missing_evidence = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarships WHERE application_url IS NULL OR trim(application_url) = ''")
    missing_app_url = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarships WHERE official_source_url IS NULL OR trim(official_source_url) = ''")
    missing_official_url = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarships WHERE deadline IS NULL")
    missing_deadline = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM scholarship_sources")
    sources_count = cursor.fetchone()[0]

    cursor.execute("SELECT count(DISTINCT scholarship_id) FROM scholarship_sources")
    scholarships_with_sources = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM verification_records")
    vr_count = cursor.fetchone()[0]

    cursor.execute("SELECT count(DISTINCT scholarship_id) FROM verification_records")
    scholarships_with_verifications = cursor.fetchone()[0]

    cursor.execute("SELECT verification_status, count(*) FROM verification_records GROUP BY verification_status")
    vr_statuses = dict(cursor.fetchall())

    cursor.execute("SELECT freshness_status, count(*) FROM verification_records GROUP BY freshness_status")
    freshness_counts = dict(cursor.fetchall())

    # Check unverified scholarships (scholarships without verification record or with UNVERIFIED status)
    cursor.execute("""
        SELECT count(*) FROM scholarships s
        LEFT JOIN (
            SELECT scholarship_id, verification_status FROM verification_records
            WHERE id IN (SELECT max(id) FROM verification_records GROUP BY scholarship_id)
        ) v ON s.id = v.scholarship_id
        WHERE v.verification_status IS NULL OR v.verification_status = 'UNVERIFIED'
    """)
    effective_unverified = cursor.fetchone()[0]

    cursor.execute("""
        SELECT v.verification_status, count(*) FROM scholarships s
        JOIN (
            SELECT scholarship_id, verification_status FROM verification_records
            WHERE id IN (SELECT max(id) FROM verification_records GROUP BY scholarship_id)
        ) v ON s.id = v.scholarship_id
        GROUP BY v.verification_status
    """)
    latest_verification_counts = dict(cursor.fetchall())

    # Check unresolved taxonomy in legacy_metadata / requirements
    # Let's inspect sample requirements and legacy_metadata
    cursor.execute("SELECT id, name, requirements, eligibility_evidence, legacy_metadata, official_source_url, application_url FROM scholarships LIMIT 5")
    samples = cursor.fetchall()

    res = {
        "total_scholarships": total_count,
        "synthetic_count": synth_count,
        "real_count": total_count - synth_count,
        "distinct_names": distinct_names,
        "duplicate_names": total_count - distinct_names,
        "data_quality_breakdown": dq_counts,
        "status_breakdown": status_counts,
        "missing_description": missing_desc,
        "missing_provider": missing_prov,
        "missing_requirements": missing_req,
        "missing_evidence": missing_evidence,
        "missing_application_url": missing_app_url,
        "missing_official_source_url": missing_official_url,
        "missing_deadline": missing_deadline,
        "total_sources_records": sources_count,
        "scholarships_with_sources": scholarships_with_sources,
        "total_verification_records": vr_count,
        "scholarships_with_verifications": scholarships_with_verifications,
        "verification_records_breakdown": vr_statuses,
        "freshness_breakdown": freshness_counts,
        "latest_verification_per_scholarship": latest_verification_counts,
        "effective_unverified_scholarships": effective_unverified,
    }
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    audit()
