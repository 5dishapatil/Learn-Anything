import sqlite3

conn = sqlite3.connect('backend/axiom.db')
c = conn.cursor()

print("Existing tables:")
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(tables)

journey_ids = list(range(1, 12))
j_str = ','.join(str(i) for i in journey_ids)
print("Cleaning test journeys:", j_str)

concept_ids = [r[0] for r in c.execute("SELECT id FROM concepts WHERE journey_id IN (" + j_str + ")").fetchall()]
print(f"Found {len(concept_ids)} concepts to clean")

project_ids = [r[0] for r in c.execute("SELECT id FROM projects WHERE journey_id IN (" + j_str + ")").fetchall()]
print(f"Found {len(project_ids)} projects to clean")

if concept_ids:
    c_str = ','.join(str(i) for i in concept_ids)
    if 'feynman_feedbacks' in tables:
        c.execute("DELETE FROM feynman_feedbacks WHERE explanation_id IN (SELECT id FROM feynman_explanations WHERE concept_id IN (" + c_str + "))")
    elif 'feynman_feedback' in tables:
        c.execute("DELETE FROM feynman_feedback WHERE explanation_id IN (SELECT id FROM feynman_explanations WHERE concept_id IN (" + c_str + "))")
    c.execute("DELETE FROM feynman_explanations WHERE concept_id IN (" + c_str + ")")
    c.execute("DELETE FROM quiz_attempts WHERE question_id IN (SELECT id FROM recall_questions WHERE concept_id IN (" + c_str + "))")
    c.execute("DELETE FROM recall_questions WHERE concept_id IN (" + c_str + ")")
    c.execute("DELETE FROM review_schedules WHERE concept_id IN (" + c_str + ")")
    c.execute("DELETE FROM flashcards WHERE concept_id IN (" + c_str + ")")
    c.execute("DELETE FROM think_deeper_responses WHERE question_id IN (SELECT id FROM think_deeper_questions WHERE concept_id IN (" + c_str + "))")
    c.execute("DELETE FROM think_deeper_questions WHERE concept_id IN (" + c_str + ")")
    c.execute("DELETE FROM research_citations WHERE lesson_section_id IN (SELECT id FROM lesson_sections WHERE lesson_id IN (SELECT id FROM lessons WHERE concept_id IN (" + c_str + ")))")
    c.execute("DELETE FROM lesson_sections WHERE lesson_id IN (SELECT id FROM lessons WHERE concept_id IN (" + c_str + "))")
    c.execute("DELETE FROM lessons WHERE concept_id IN (" + c_str + ")")
    c.execute("DELETE FROM concept_dependencies WHERE source_concept_id IN (" + c_str + ") OR target_concept_id IN (" + c_str + ")")
    c.execute("DELETE FROM concepts WHERE id IN (" + c_str + ")")

if project_ids:
    p_str = ','.join(str(i) for i in project_ids)
    c.execute("DELETE FROM experiment_results WHERE experiment_id IN (SELECT id FROM experiments WHERE project_id IN (" + p_str + "))")
    c.execute("DELETE FROM experiments WHERE project_id IN (" + p_str + ")")
    c.execute("DELETE FROM project_tasks WHERE milestone_id IN (SELECT id FROM project_milestones WHERE project_id IN (" + p_str + "))")
    c.execute("DELETE FROM project_milestones WHERE project_id IN (" + p_str + ")")
    c.execute("DELETE FROM project_artifacts WHERE project_id IN (" + p_str + ")")
    c.execute("DELETE FROM projects WHERE id IN (" + p_str + ")")

c.execute("DELETE FROM learning_tasks WHERE journey_id IN (" + j_str + ")")
c.execute("DELETE FROM learning_modules WHERE road_id IN (SELECT id FROM learning_roads WHERE journey_id IN (" + j_str + "))")
c.execute("DELETE FROM learning_roads WHERE journey_id IN (" + j_str + ")")
c.execute("DELETE FROM learning_blueprints WHERE journey_id IN (" + j_str + ")")
c.execute("DELETE FROM progress_events WHERE journey_id IN (" + j_str + ")")
c.execute("DELETE FROM notes WHERE journey_id IN (" + j_str + ")")
c.execute("DELETE FROM learning_journeys WHERE id IN (" + j_str + ")")

# Fix Journey 13 title and domain
c.execute("""
    UPDATE learning_journeys
    SET title = 'Brain-Computer Interfaces & Computational Neuroscience',
        subject_domain = 'Computational Neuroscience & Neural Engineering',
        final_project_goal = 'Build a real-time EEG/neural signal decoding pipeline and spike-sorting model.'
    WHERE id = 13
""")

conn.commit()
print("Clean complete! Remaining journeys:")
for r in c.execute("SELECT id, title, user_intent FROM learning_journeys").fetchall():
    print(r)
conn.close()
