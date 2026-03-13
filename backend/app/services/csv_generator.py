
import csv
import io


def generate_csv(analysis: dict) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)

    # Sheet 1: Summary
    writer.writerow(["Summary"])
    writer.writerow(["analysis_id", analysis["analysis_id"]])
    writer.writerow(["total_responses", analysis["summary"]["total_responses"]])
    writer.writerow(["num_topics", analysis["summary"]["num_topics"]])
    writer.writerow([])

    # Section 2: Topics
    writer.writerow(["Topics"])
    writer.writerow(["topic_id", "label"])
    for topic in analysis.get("topics", []):
        writer.writerow([topic["topic_id"], topic["label"]])
    writer.writerow([])

    # Section 3: Assignments
    writer.writerow(["Assignments"])
    writer.writerow(["text", "topic_id", "topic_label"])
    for assignment in analysis.get("assignments", []):
        writer.writerow([
            assignment["text"],
            assignment["topic_id"],
            assignment["topic_label"],
        ])

    return output.getvalue().encode("utf-8")
