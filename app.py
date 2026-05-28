"""
College Event Registration & Attendance Analytics Platform
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import os
import io
import sys

# ── Page configuration (must be first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title=" College Event Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from database.db import init_db, reset_db, get_connection, get_table_counts
from processing.clean import clean_registrations, clean_attendance
from processing.validate import validate_emails, validate_required_fields, detect_duplicates
from processing.transform import apply_all_transformations
from processing.match import match_attendance
from processing.load import load_students, load_events, load_registrations, load_attendance, load_invalid_records
from analytics.reports import (
    registrations_per_event, attendance_per_event, attendance_percentage,
    department_participation, year_wise_participation, top_attended_events,
    invalid_records_summary, overall_stats,
)
from analytics.attendance_analysis import (
    get_match_summary, get_attendance_trends, get_department_leaderboard,
    get_event_department_heatmap,
)
from charts.charts import (
    bar_registrations_vs_attendance, pie_department_participation,
    bar_attendance_percentage, bar_year_wise, bar_top_events,
    pie_invalid_records, line_attendance_trends, heatmap_event_department,
    bar_department_leaderboard, bar_match_summary,
)
from utils.sample_data import generate_sample_registrations, generate_sample_attendance, get_sample_csv_bytes





# ── Session State Initialization ──────────────────────────────────────────────
def init_session_state():
    defaults = {
        "reg_raw": None,
        "att_raw": None,
        "reg_cleaned": None,
        "att_cleaned": None,
        "invalid_emails_reg": None,
        "invalid_emails_att": None,
        "missing_fields_reg": None,
        "missing_fields_att": None,
        "duplicates_reg": None,
        "duplicates_att": None,
        "match_results": None,
        "processed": False,
        "invalid_records_list": [],
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

init_session_state()


# ── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0;">
        <h1 style="font-size: 2rem; margin-bottom: 4px;"></h1>
        <h2 style="font-size: 1.1rem; margin: 0;">Event Analytics</h2>
        <p style="color: #94A3B8; font-size: 0.8rem; margin-top: 4px;">Registration & Attendance Platform</p>
    </div>
    """, unsafe_allow_html=True)

    

    page = st.radio(
        "Navigation",
        [
            "Upload & Process",
            "Raw Data",
            "Cleaned Data",
            "Invalid Records",
            "Dashboard",
            "Export",
        ],
        label_visibility="collapsed",
    )

    

    # Database info
    if st.session_state.processed:
        try:
            conn = get_connection()
            counts = get_table_counts(conn)
            conn.close()
            st.markdown("##### Database Status")
            for table, count in counts.items():
                st.caption(f"• {table}: **{count}** rows")
        except Exception:
            pass

    
    st.caption("Built with Streamlit + Plotly")
    st.caption("© 2025 College Event Analytics")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Upload & Process
# ══════════════════════════════════════════════════════════════════════════════
if page == "Upload & Process":
    st.markdown("# Upload & Process Data")
    st.markdown("Upload your registration and attendance CSV files, or generate sample data to get started.")

    # ── Sample Data Generator ─────────────────────────────────────────────
    with st.expander("Generate Sample Data", expanded=not st.session_state.processed):
        st.markdown("Generate realistic demo datasets with intentional messy data for testing.")
        col1, col2 = st.columns(2)
        with col1:
            num_records = st.slider("Number of registration records", 50, 300, 160, step=10)
        with col2:
            st.markdown("")
            st.markdown("")
            generate_btn = st.button("Generate Sample Data", use_container_width=True)

        if generate_btn:
            with st.spinner("Generating sample datasets..."):
                reg_sample = generate_sample_registrations(num_records)
                att_sample = generate_sample_attendance(reg_sample)
                st.session_state.reg_raw = reg_sample
                st.session_state.att_raw = att_sample
                st.success(f"Generated {len(reg_sample)} registration records & {len(att_sample)} attendance records!")

            # Show download buttons for sample data
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "Download Sample Registrations CSV",
                    get_sample_csv_bytes(st.session_state.reg_raw),
                    "sample_registrations.csv",
                    "text/csv",
                    use_container_width=True,
                )
            with c2:
                st.download_button(
                    "Download Sample Attendance CSV",
                    get_sample_csv_bytes(st.session_state.att_raw),
                    "sample_attendance.csv",
                    "text/csv",
                    use_container_width=True,
                )

    

    # ── File Upload ───────────────────────────────────────────────────────
    st.markdown("### Upload CSV Files")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Registration CSV**")
        reg_file = st.file_uploader(
            "Upload Registration CSV",
            type=["csv"],
            key="reg_uploader",
            label_visibility="collapsed",
        )
        if reg_file:
            st.session_state.reg_raw = pd.read_csv(reg_file)
            st.success(f"Loaded {len(st.session_state.reg_raw)} registration records")

    with col2:
        st.markdown("**Attendance CSV**")
        att_file = st.file_uploader(
            "Upload Attendance CSV",
            type=["csv"],
            key="att_uploader",
            label_visibility="collapsed",
        )
        if att_file:
            st.session_state.att_raw = pd.read_csv(att_file)
            st.success(f"Loaded {len(st.session_state.att_raw)} attendance records")

    

    # ── Process Button ────────────────────────────────────────────────────
    if st.session_state.reg_raw is not None and st.session_state.att_raw is not None:
        st.markdown("### Process Data Pipeline")
        st.markdown("This will **clean → validate → transform → match → load** your data into the database.")

        if st.button("Run Full Pipeline", use_container_width=True, type="primary"):
            progress = st.progress(0, text="Initializing...")
            invalid_records = []

            try:
                # Step 1: Init DB
                progress.progress(5, text="Initializing database...")
                reset_db()
                init_db()

                # Step 2: Clean
                progress.progress(15, text="Cleaning data...")
                reg_cleaned = clean_registrations(st.session_state.reg_raw.copy())
                att_cleaned = clean_attendance(st.session_state.att_raw.copy())

                # Step 3: Transform
                progress.progress(25, text="Normalizing event & department names...")
                reg_cleaned = apply_all_transformations(reg_cleaned, is_registration=True)
                att_cleaned = apply_all_transformations(att_cleaned, is_registration=False)

                # Step 4: Validate — Missing Fields (Registration)
                progress.progress(35, text="Validating required fields...")
                reg_required = ["registration_id", "student_name", "email", "department", "year", "event_name"]
                reg_cleaned, missing_reg = validate_required_fields(reg_cleaned, reg_required)
                if len(missing_reg) > 0:
                    for _, row in missing_reg.iterrows():
                        invalid_records.append({
                            "source": "registration",
                            "row_data": row.to_dict(),
                            "reason": "missing_required_field",
                        })
                st.session_state.missing_fields_reg = missing_reg

                # Validate — Missing Fields (Attendance)
                att_required = ["email", "event_name", "attendance_status"]
                att_cleaned, missing_att = validate_required_fields(att_cleaned, att_required)
                if len(missing_att) > 0:
                    for _, row in missing_att.iterrows():
                        invalid_records.append({
                            "source": "attendance",
                            "row_data": row.to_dict(),
                            "reason": "missing_required_field",
                        })
                st.session_state.missing_fields_att = missing_att

                # Step 5: Validate — Emails
                progress.progress(45, text="Validating email addresses...")
                reg_cleaned, invalid_emails_reg = validate_emails(reg_cleaned, "email")
                if len(invalid_emails_reg) > 0:
                    for _, row in invalid_emails_reg.iterrows():
                        invalid_records.append({
                            "source": "registration",
                            "row_data": row.to_dict(),
                            "reason": "invalid_email",
                        })
                st.session_state.invalid_emails_reg = invalid_emails_reg

                att_cleaned, invalid_emails_att = validate_emails(att_cleaned, "email")
                if len(invalid_emails_att) > 0:
                    for _, row in invalid_emails_att.iterrows():
                        invalid_records.append({
                            "source": "attendance",
                            "row_data": row.to_dict(),
                            "reason": "invalid_email",
                        })
                st.session_state.invalid_emails_att = invalid_emails_att

                # Step 6: Detect Duplicates
                progress.progress(55, text="Detecting duplicates...")
                reg_cleaned, dup_reg = detect_duplicates(reg_cleaned, ["email", "event_name"])
                if len(dup_reg) > 0:
                    for _, row in dup_reg.iterrows():
                        invalid_records.append({
                            "source": "registration",
                            "row_data": row.to_dict(),
                            "reason": "duplicate_registration",
                        })
                st.session_state.duplicates_reg = dup_reg

                att_cleaned_dedup, dup_att = detect_duplicates(att_cleaned, ["email", "event_name"])
                if len(dup_att) > 0:
                    for _, row in dup_att.iterrows():
                        invalid_records.append({
                            "source": "attendance",
                            "row_data": row.to_dict(),
                            "reason": "duplicate_attendance",
                        })
                st.session_state.duplicates_att = dup_att

                # Step 7: Match Attendance
                progress.progress(65, text="Matching attendance against registrations...")
                match_results = match_attendance(reg_cleaned, att_cleaned)
                st.session_state.match_results = match_results

                # Log unregistered attendees
                unreg = match_results["attended_without_registration"]
                if len(unreg) > 0:
                    for _, row in unreg.iterrows():
                        invalid_records.append({
                            "source": "attendance",
                            "row_data": row.to_dict(),
                            "reason": "attended_without_registration",
                        })

                # Step 8: Store cleaned data
                st.session_state.reg_cleaned = reg_cleaned
                st.session_state.att_cleaned = att_cleaned

                # Step 9: Load into DB
                progress.progress(75, text="Loading data into SQLite...")
                conn = get_connection()
                load_students(conn, reg_cleaned)
                load_events(conn, reg_cleaned, att_cleaned)
                load_registrations(conn, reg_cleaned)
                load_attendance(conn, att_cleaned)

                # Step 10: Load invalid records
                progress.progress(90, text="Storing invalid records...")
                st.session_state.invalid_records_list = invalid_records
                load_invalid_records(conn, invalid_records)
                conn.close()

                # Done
                progress.progress(100, text="Pipeline complete!")
                st.session_state.processed = True

                # Summary

                
                st.markdown("### Pipeline Summary")
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Clean Registrations", len(reg_cleaned))
                s2.metric("Clean Attendance", len(att_cleaned))
                s3.metric("Invalid Records", len(invalid_records))
                s4.metric("Duplicates Found", len(dup_reg) + len(dup_att))

            except Exception as e:
                st.error(f"Pipeline failed: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    elif st.session_state.reg_raw is None and st.session_state.att_raw is None:
        st.info("Upload CSV files or generate sample data to begin.")
    elif st.session_state.reg_raw is None:
        st.warning("Registration CSV is missing. Please upload it above.")
    else:
        st.warning("Attendance CSV is missing. Please upload it above.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Raw Data
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Raw Data":
    st.markdown("# Raw Uploaded Data")

    if st.session_state.reg_raw is not None:
        st.markdown("### Registration Data (Raw)")
        st.markdown(f"**{len(st.session_state.reg_raw)} rows** × **{len(st.session_state.reg_raw.columns)} columns**")
        st.dataframe(st.session_state.reg_raw, use_container_width=True, height=400)
    else:
        st.info("No registration data uploaded yet.")

    

    if st.session_state.att_raw is not None:
        st.markdown("### Attendance Data (Raw)")
        st.markdown(f"**{len(st.session_state.att_raw)} rows** × **{len(st.session_state.att_raw.columns)} columns**")
        st.dataframe(st.session_state.att_raw, use_container_width=True, height=400)
    else:
        st.info("No attendance data uploaded yet.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Cleaned Data
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Cleaned Data":
    st.markdown("# Cleaned & Transformed Data")

    if not st.session_state.processed:
        st.warning("Please process the data first on the Upload page.")
    else:
        # Before / After metrics
        st.markdown("### Cleaning Impact")
        c1, c2, c3 = st.columns(3)
        raw_reg_count = len(st.session_state.reg_raw) if st.session_state.reg_raw is not None else 0
        clean_reg_count = len(st.session_state.reg_cleaned) if st.session_state.reg_cleaned is not None else 0
        raw_att_count = len(st.session_state.att_raw) if st.session_state.att_raw is not None else 0
        clean_att_count = len(st.session_state.att_cleaned) if st.session_state.att_cleaned is not None else 0
        removed = (raw_reg_count - clean_reg_count) + (raw_att_count - clean_att_count)

        c1.metric("Raw Records", raw_reg_count + raw_att_count)
        c2.metric("Clean Records", clean_reg_count + clean_att_count)
        c3.metric("Records Removed", removed)

        

        if st.session_state.reg_cleaned is not None:
            st.markdown("### Cleaned Registrations")
            st.dataframe(st.session_state.reg_cleaned, use_container_width=True, height=400)

        

        if st.session_state.att_cleaned is not None:
            st.markdown("### Cleaned Attendance")
            st.dataframe(st.session_state.att_cleaned, use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Invalid Records
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Invalid Records":
    st.markdown("# Invalid & Problematic Records")

    if not st.session_state.processed:
        st.warning("Please process the data first on the Upload page.")
    else:
        # Summary metric
        total_invalid = len(st.session_state.invalid_records_list)
        st.metric("Total Invalid Records", total_invalid)
        

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Invalid Emails",
            "Duplicates",
            "Missing Fields",
            "Unmatched Attendance",
            "Summary",
        ])

        with tab1:
            st.markdown("### Invalid Email Addresses")
            inv_reg = st.session_state.invalid_emails_reg
            inv_att = st.session_state.invalid_emails_att
            if inv_reg is not None and len(inv_reg) > 0:
                st.markdown(f"**Registration:** {len(inv_reg)} invalid emails")
                st.dataframe(inv_reg, use_container_width=True)
            else:
                st.success("No invalid emails in registrations.")

            if inv_att is not None and len(inv_att) > 0:
                st.markdown(f"**Attendance:** {len(inv_att)} invalid emails")
                st.dataframe(inv_att, use_container_width=True)
            else:
                st.success("No invalid emails in attendance.")

        with tab2:
            st.markdown("### Duplicate Records")
            dup_reg = st.session_state.duplicates_reg
            dup_att = st.session_state.duplicates_att
            if dup_reg is not None and len(dup_reg) > 0:
                st.markdown(f"**Registration Duplicates:** {len(dup_reg)} records")
                st.dataframe(dup_reg, use_container_width=True)
            else:
                st.success("No duplicate registrations found.")

            if dup_att is not None and len(dup_att) > 0:
                st.markdown(f"**Attendance Duplicates:** {len(dup_att)} records")
                st.dataframe(dup_att, use_container_width=True)
            else:
                st.success("No duplicate attendance records found.")

        with tab3:
            st.markdown("### Missing Required Fields")
            miss_reg = st.session_state.missing_fields_reg
            miss_att = st.session_state.missing_fields_att
            if miss_reg is not None and len(miss_reg) > 0:
                st.markdown(f"**Registration:** {len(miss_reg)} records with missing fields")
                st.dataframe(miss_reg, use_container_width=True)
            else:
                st.success("No missing fields in registrations.")

            if miss_att is not None and len(miss_att) > 0:
                st.markdown(f"**Attendance:** {len(miss_att)} records with missing fields")
                st.dataframe(miss_att, use_container_width=True)
            else:
                st.success("No missing fields in attendance.")

        with tab4:
            st.markdown("### Attendance Matching Issues")
            if st.session_state.match_results:
                mr = st.session_state.match_results

                st.markdown("#### Registered & Attended")
                st.metric("Count", len(mr["registered_and_attended"]))
                if len(mr["registered_and_attended"]) > 0:
                    with st.expander("View records"):
                        st.dataframe(mr["registered_and_attended"], use_container_width=True)

                st.markdown("#### Registered but Absent")
                st.metric("Count", len(mr["registered_but_absent"]))
                if len(mr["registered_but_absent"]) > 0:
                    with st.expander("View records"):
                        st.dataframe(mr["registered_but_absent"], use_container_width=True)

                st.markdown("#### Attended without Registration")
                st.metric("Count", len(mr["attended_without_registration"]))
                if len(mr["attended_without_registration"]) > 0:
                    with st.expander("View records"):
                        st.dataframe(mr["attended_without_registration"], use_container_width=True)

                st.markdown("#### Duplicate Attendance")
                st.metric("Count", len(mr["duplicate_attendance"]))
                if len(mr["duplicate_attendance"]) > 0:
                    with st.expander("View records"):
                        st.dataframe(mr["duplicate_attendance"], use_container_width=True)
            else:
                st.info("No matching results available.")

        with tab5:
            st.markdown("### Invalid Records Summary")
            try:
                conn = get_connection()
                inv_summary = invalid_records_summary(conn)
                conn.close()
                if len(inv_summary) > 0:
                    st.dataframe(inv_summary, use_container_width=True)
                    fig = pie_invalid_records(inv_summary)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("No invalid records!")
            except Exception:
                st.info("Database not available. Process data first.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Dashboard":
    st.markdown("# Analytics Dashboard")

    if not st.session_state.processed:
        st.warning("Please process the data first on the Upload page.")
    else:
        try:
            conn = get_connection()

            # ── KPI Metrics ───────────────────────────────────────────────
            stats = overall_stats(conn)
            st.markdown("### Key Metrics")
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Students", stats["students"])
            k2.metric("Events", stats["events"])
            k3.metric("Registrations", stats["registrations"])
            k4.metric("Attendance", stats["attendance"])
            k5.metric("Attendance Rate", f"{stats['overall_attendance_rate']}%")

            

            # ── Tab-based dashboard ───────────────────────────────────────
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Event Analytics",
                "Department Analytics",
                "Year-wise Analytics",
                "Matching Analysis",
                "Advanced",
            ])

            with tab1:
                st.markdown("### Event-wise Analytics")
                reg_per_event = registrations_per_event(conn)
                att_per_event = attendance_per_event(conn)
                pct = attendance_percentage(conn)
                top_events = top_attended_events(conn, 5)

                col1, col2 = st.columns(2)
                with col1:
                    if not reg_per_event.empty and not att_per_event.empty:
                        fig = bar_registrations_vs_attendance(reg_per_event, att_per_event)
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    if not pct.empty:
                        fig = bar_attendance_percentage(pct)
                        st.plotly_chart(fig, use_container_width=True)

                
                if not top_events.empty:
                    fig = bar_top_events(top_events)
                    st.plotly_chart(fig, use_container_width=True)

                # Data tables
                with st.expander("View Event Data Tables"):
                    st.markdown("**Registrations Per Event**")
                    st.dataframe(reg_per_event, use_container_width=True)
                    st.markdown("**Attendance Percentage**")
                    st.dataframe(pct, use_container_width=True)

            with tab2:
                st.markdown("### Department Analytics")
                dept_data = department_participation(conn)
                dept_lb = get_department_leaderboard(conn)

                col1, col2 = st.columns(2)
                with col1:
                    if not dept_data.empty:
                        fig = pie_department_participation(dept_data)
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    if not dept_lb.empty:
                        fig = bar_department_leaderboard(dept_lb)
                        st.plotly_chart(fig, use_container_width=True)

                with st.expander("View Department Data"):
                    st.markdown("**Department Participation**")
                    st.dataframe(dept_data, use_container_width=True)
                    st.markdown("**Department Leaderboard**")
                    st.dataframe(dept_lb, use_container_width=True)

            with tab3:
                st.markdown("### Year-wise Participation")
                year_data = year_wise_participation(conn)
                if not year_data.empty:
                    fig = bar_year_wise(year_data)
                    st.plotly_chart(fig, use_container_width=True)
                    with st.expander("View Year-wise Data"):
                        st.dataframe(year_data, use_container_width=True)
                else:
                    st.info("No year-wise data available.")

            with tab4:
                st.markdown("### Registration vs Attendance Matching")
                match_summary = get_match_summary(conn)
                trends = get_attendance_trends(conn)

                col1, col2 = st.columns(2)
                with col1:
                    if not match_summary.empty:
                        fig = bar_match_summary(match_summary)
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    if not trends.empty:
                        fig = line_attendance_trends(trends)
                        st.plotly_chart(fig, use_container_width=True)

                with st.expander("View Match Data"):
                    st.dataframe(match_summary, use_container_width=True)

            with tab5:
                st.markdown("### Advanced Analytics")

                # Heatmap
                heatmap_data = get_event_department_heatmap(conn)
                if not heatmap_data.empty:
                    fig = heatmap_event_department(heatmap_data)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for heatmap.")

                

                # Invalid records summary
                st.markdown("### Data Quality Summary")
                inv_summary = invalid_records_summary(conn)
                if not inv_summary.empty:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.dataframe(inv_summary, use_container_width=True)
                    with col2:
                        fig = pie_invalid_records(inv_summary)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("No data quality issues!")

            conn.close()

        except Exception as e:
            st.error(f"Dashboard error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Export
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Export":
    st.markdown("# Export Data & Reports")

    if not st.session_state.processed:
        st.warning("Please process the data first on the Upload page.")
    else:
        st.markdown("### Download Cleaned Datasets")
        col1, col2 = st.columns(2)

        with col1:
            if st.session_state.reg_cleaned is not None:
                csv_bytes = st.session_state.reg_cleaned.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Cleaned Registrations (CSV)",
                    csv_bytes,
                    "cleaned_registrations.csv",
                    "text/csv",
                    use_container_width=True,
                )

        with col2:
            if st.session_state.att_cleaned is not None:
                csv_bytes = st.session_state.att_cleaned.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Cleaned Attendance (CSV)",
                    csv_bytes,
                    "cleaned_attendance.csv",
                    "text/csv",
                    use_container_width=True,
                )

        

        st.markdown("### Download Analytics Reports (Excel)")
        if st.button("Generate Excel Report", use_container_width=True):
            try:
                conn = get_connection()
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    registrations_per_event(conn).to_excel(writer, sheet_name="Registrations Per Event", index=False)
                    attendance_per_event(conn).to_excel(writer, sheet_name="Attendance Per Event", index=False)
                    attendance_percentage(conn).to_excel(writer, sheet_name="Attendance Percentage", index=False)
                    department_participation(conn).to_excel(writer, sheet_name="Department Participation", index=False)
                    year_wise_participation(conn).to_excel(writer, sheet_name="Year-wise Participation", index=False)
                    top_attended_events(conn).to_excel(writer, sheet_name="Top Events", index=False)
                    get_match_summary(conn).to_excel(writer, sheet_name="Match Summary", index=False)
                    get_department_leaderboard(conn).to_excel(writer, sheet_name="Dept Leaderboard", index=False)
                    invalid_records_summary(conn).to_excel(writer, sheet_name="Invalid Records", index=False)
                conn.close()

                st.download_button(
                    "Download Excel Report",
                    output.getvalue(),
                    "event_analytics_report.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
                st.success("Excel report generated!")
            except Exception as e:
                st.error(f"Report generation failed: {str(e)}")

        

        st.markdown("### Download Invalid Records")
        if st.session_state.invalid_records_list:
            inv_df = pd.DataFrame([
                {"source": r["source"], "reason": r["reason"], "row_data": str(r["row_data"])}
                for r in st.session_state.invalid_records_list
            ])
            csv_bytes = inv_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Invalid Records (CSV)",
                csv_bytes,
                "invalid_records.csv",
                "text/csv",
                use_container_width=True,
            )
        else:
            st.success("No invalid records to export.")
