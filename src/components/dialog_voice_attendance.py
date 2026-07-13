import streamlit as st
import pandas as pd
from datetime import datetime

from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from src.components.dialog_attendance_results import show_attendance_result


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):

    st.write(
        "🎤 Record audio of students saying 'I am present'. "
        "The AI will recognize the enrolled students."
    )

    audio_data = st.audio_input("Record classroom audio")

    if st.button("Analyze Audio", use_container_width=True, type="primary"):

        # Make sure audio has been recorded
        if audio_data is None:
            st.warning("⚠️ Please record classroom audio before analyzing.")
            return

        with st.spinner("Processing audio..."):

            enrolled_res = (
                supabase.table("subject_students")
                .select("*, students(*)")
                .eq("subject_id", selected_subject_id)
                .execute()
            )

            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning("No students enrolled in this course.")
                return

            # Build dictionary of voice embeddings
            candidates_dict = {}

            for student in enrolled_students:
                student_data = student.get("students")

                if (
                    student_data
                    and student_data.get("voice_embedding")
                ):
                    candidates_dict[
                        student_data["student_id"]
                    ] = student_data["voice_embedding"]

            if not candidates_dict:
                st.error("No enrolled students have registered voice profiles.")
                return

            try:
                audio_bytes = audio_data.read()

                if not audio_bytes:
                    st.error("Recorded audio is empty. Please record again.")
                    return

            except Exception as e:
                st.error(f"Unable to read recorded audio.\n\n{e}")
                return

            # Voice recognition
            detected_scores = process_bulk_audio(
                audio_bytes,
                candidates_dict
            )

            if detected_scores is None:
                detected_scores = {}

            results = []
            attendance_to_log = []

            current_timestamp = datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S"
            )

            for node in enrolled_students:

                student = node["students"]

                score = detected_scores.get(
                    student["student_id"],
                    0.0
                )

                is_present = score > 0

                results.append(
                    {
                        "Name": student["name"],
                        "ID": student["student_id"],
                        "Score": round(score, 3),
                        "Status": "✅ Present" if is_present else "❌ Absent",
                    }
                )

                attendance_to_log.append(
                    {
                        "student_id": student["student_id"],
                        "subject_id": selected_subject_id,
                        "timestamp": current_timestamp,
                        "is_present": is_present,
                    }
                )

            st.session_state.voice_attendance_results = (
                pd.DataFrame(results),
                attendance_to_log,
            )

            st.rerun()

    # Show results if available
    if "voice_attendance_results" in st.session_state:

        st.divider()

        df_results, logs = st.session_state.voice_attendance_results

        show_attendance_result(df_results, logs)