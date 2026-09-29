from flask import Flask, render_template, request, redirect, make_response
import os
import sqlite3
import sys
import uuid
from pathlib import Path


# =========================================================
# EDGEONE / PATH SETUP
# =========================================================
# This file is deployed from: cloud-functions/api/[[default]].py
# The maths data file is one level above this file, inside
# cloud-functions/. The templates and static files are inside
# cloud-functions/api/templates/ and cloud-functions/api/static/.

APP_DIR = Path(__file__).resolve().parent
FUNCTIONS_DIR = APP_DIR.parent
PROJECT_DIR = FUNCTIONS_DIR.parent

# Make cloud-functions available for the maths_data import.
if str(FUNCTIONS_DIR) not in sys.path:
    sys.path.insert(0, str(FUNCTIONS_DIR))

from maths_data import (
    maths_structure,
    maths_videos,
    maths_notes,
    maths_sheets,
    maths_overview
)


# Explicitly point Flask at the folders that actually exist in the
# EdgeOne Cloud Function package.
app = Flask(
    __name__,
    template_folder=str(APP_DIR / "templates"),
    static_folder=str(APP_DIR / "static")
)


# Locally, keep using the project's existing database. On EdgeOne,
# the project-root database may not be included in the function
# package, so use a writable temporary location unless DATABASE_PATH
# is explicitly supplied.
configured_database = os.environ.get("DATABASE_PATH")
local_database = PROJECT_DIR / "selectionday.db"
seed_database = FUNCTIONS_DIR / "selectionday.db"
edge_database = Path("/tmp/selectionday.db")

if configured_database:
    DATABASE = configured_database
elif os.name == "nt":
    # Local Windows development: use the original project database.
    DATABASE = str(local_database)
else:
    # EdgeOne runs Linux functions from a deployed, non-writable package.
    # Use /tmp for the SQLite working copy and seed it from the packaged DB.
    # This prevents SQLite from trying to write into the deployed package.
    if not edge_database.exists() and seed_database.exists():
        import shutil
        shutil.copy2(seed_database, edge_database)
    DATABASE = str(edge_database)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            browser_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            PRIMARY KEY (browser_id, course_id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS completed_videos (
            browser_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            video_index INTEGER NOT NULL,
            PRIMARY KEY (browser_id, course_id, video_index)
        )
    """)

    connection.commit()
    connection.close()


def get_browser_id():
    browser_id = request.cookies.get("selectionday_browser_id")

    if not browser_id:
        browser_id = str(uuid.uuid4())

    return browser_id


def set_browser_cookie(response, browser_id):
    response.set_cookie(
        "selectionday_browser_id",
        browser_id,
        max_age=60 * 60 * 24 * 365 * 5
    )

    return response


# =========================================================
# COURSES
# =========================================================

courses = [

    {
        "id": "history",
        "name": "History",
        "description": "Learn Ancient, Medieval and Modern History."
    },

    {
        "id": "geography",
        "name": "Geography",
        "description": "Learn Physical, Indian and World Geography."
    },

    {
        "id": "polity",
        "name": "Polity",
        "description": "Learn the Constitution and Indian Political System."
    },

    {
        "id": "economics",
        "name": "Economics",
        "description": "Learn Indian Economy and Economic Concepts."
    },

    {
        "id": "maths",
        "name": "Maths",
        "description": "Complete Mathematics for competitive exams."
    },

    {
        "id": "reasoning",
        "name": "Reasoning",
        "description": "Verbal and Non-Verbal Reasoning preparation."
    },

    {
        "id": "english",
        "name": "English",
        "description": "Grammar, vocabulary and comprehension."
    },

    {
        "id": "hindi",
        "name": "Hindi",
        "description": "Hindi grammar and competitive exam preparation."
    },

    {
        "id": "science",
        "name": "General Science",
        "description": "Physics, Chemistry and Biology."
    },

    {
        "id": "computer",
        "name": "Computer",
        "description": "Computer fundamentals and awareness."
    },

    {
        "id": "current-affairs",
        "name": "Current Affairs",
        "description": "Current affairs and general awareness."
    },

    {
        "id": "verbal",
        "name": "Verbal",
        "description": "Verbal ability and competitive English."
    },

    {
        "id": "non-verbal",
        "name": "Non-Verbal",
        "description": "Non-Verbal Reasoning practice."
    }

]


# =========================================================
# VIDEO QUALITY HELPER
# =========================================================

def make_quality_urls(url):
    return {
        "720p": url,
        "480p": url.replace("720p", "480p"),
        "360p": url.replace("720p", "360p"),
        "240p": url.replace("720p", "240p")
    }


# =========================================================
# HISTORY 720P URLS
# =========================================================

history_720p_urls = [

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69db849622cc6f4d5f46d78a/output_720p.mp4",

    "https://selectionwayrecordedmp4-proxy2.hranker.com:8443/561/69dcc74422cc6f4d5f58a409/mp4/varun_history_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69ded95a22cc6f4d5f6a55c0/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69e01a4c22cc6f4d5f726425/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69e2d54622cc6f4d5f88e5fe/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69e5768522cc6f4d5f8c082d/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69e6c81822cc6f4d5f9edaa0/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69e185c722cc6f4d5f7eaa05/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69eac35d22cc6f4d5fc9e465/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69ec1d8422cc6f4d5fde180a/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69f08b7e22cc6f4d5f0e6189/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69f262be22cc6f4d5f43934d/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69f540c622cc6f4d5f5afa0b/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69fa37b20e57144133ebe2cd/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69fbe021b927c1a84a24a877/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69fd24adb927c1a84a2befc4/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69fe6e71b927c1a84a35bd68/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a00e60bb927c1a84a407ae8/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a01a46bb927c1a84a4bd8dd/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a03c0ebb927c1a84a684e69/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a059e24b927c1a84a82123a/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a085283b927c1a84aabc495/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a18ee39b927c1a84a6e9bc7/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a1dde3db927c1a84a9e14a2/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a20cf62b927c1a84acf4815/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a225e6ab927c1a84adad81f/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a259e55b927c1a84aeb26b4/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a27596cb927c1a84a1428cc/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a27eae6b927c1a84a1f34b3/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a294446b927c1a84a2db9ed/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/69713f3d719de161ee12bb05/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6971f599719de161ee28df0c/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6978e132c566674bff8dc882/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a38785db927c1a84ac52abf/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a39e836b927c1a84ae02604/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a3b69c5b927c1a84a0023f8/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6a3cbf8db927c1a84a1b6908/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/697faa0c4ca8c7fbe8fc2215/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/698071144ca8c7fbe80133b4/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6981ca7c4ca8c7fbe8117646/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/698318e3fc5097091c063a19/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6984559cfdd21a8a2d13c3be/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6988e3d55b61b5fe0001afdf/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/6989a7a55b61b5fe00084325/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/698b7281a003679fb8ace838/output_720p.mp4",

    "https://selectionwayrecorded-proxy2.hranker.com:8443/698c7079a003679fb8c0391c/output_720p.mp4"

]


# =========================================================
# VIDEOS
# =========================================================

videos = {

    "history": [
        {
            "title": f"History Class {i:02d}",
            "teacher": "Varun Sir",
            "quality": make_quality_urls(url)
        }
        for i, url in enumerate(history_720p_urls, start=1)
    ],

    "geography": [
        {
            "title": "Geography Class 01",
            "teacher": "Faculty",
            "quality": {
                "720p": "#",
                "480p": "#",
                "360p": "#",
                "240p": "#"
            }
        }
    ],

    "polity": [
        {
            "title": "Polity Class 01",
            "teacher": "Faculty",
            "quality": {
                "720p": "#",
                "480p": "#",
                "360p": "#",
                "240p": "#"
            }
        }
    ],

    "economics": [
        {
            "title": "Economics Class 01",
            "teacher": "Faculty",
            "quality": {
                "720p": "#",
                "480p": "#",
                "360p": "#",
                "240p": "#"
            }
        }
    ]
}


# =========================================================
# NOTES
# =========================================================

notes = {

    "history": [
        {
            "title": "History Notes 01",
            "url": "#"
        },
        {
            "title": "History Notes 02",
            "url": "#"
        },
        {
            "title": "Practice Sheet 01",
            "url": "#"
        }
    ],

    "geography": [
        {
            "title": "Geography Notes 01",
            "url": "#"
        },
        {
            "title": "Geography Notes 02",
            "url": "#"
        }
    ],

    "polity": [
        {
            "title": "Polity Notes 01",
            "url": "#"
        }
    ],

    "economics": [
        {
            "title": "Economics Notes 01",
            "url": "#"
        }
    ]

}



# =========================================================
# MATHS DATA
# =========================================================

videos["maths"] = maths_videos
notes["maths"] = maths_notes



# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    browser_id = get_browser_id()

    selected_filter = request.args.get(
        "filter",
        "all"
    )

    connection = get_db()

    enrolled_rows = connection.execute(
        """
        SELECT course_id
        FROM enrollments
        WHERE browser_id = ?
        """,
        (browser_id,)
    ).fetchall()

    enrolled_ids = {
        row["course_id"]
        for row in enrolled_rows
    }

    connection.close()

    if selected_filter == "enrolled":

        displayed_courses = [
            course
            for course in courses
            if course["id"] in enrolled_ids
        ]

    else:

        displayed_courses = courses

    response = make_response(
        render_template(
            "index.html",
            courses=displayed_courses,
            course_count=len(courses),
            enrolled_count=len(enrolled_ids),
            selected_filter=selected_filter
        )
    )

    return set_browser_cookie(
        response,
        browser_id
    )


# =========================================================
# MY COURSES
# =========================================================

@app.route("/my-courses")
def my_courses():

    browser_id = get_browser_id()

    connection = get_db()

    enrolled_rows = connection.execute(
        """
        SELECT course_id
        FROM enrollments
        WHERE browser_id = ?
        """,
        (browser_id,)
    ).fetchall()

    enrolled_ids = {
        row["course_id"]
        for row in enrolled_rows
    }

    connection.close()

    my_courses_list = []

    for course in courses:

        if course["id"] not in enrolled_ids:
            continue

        course_videos = videos.get(
            course["id"],
            []
        )

        total = len(course_videos)

        connection = get_db()

        completed_row = connection.execute(
            """
            SELECT COUNT(*) AS completed
            FROM completed_videos
            WHERE browser_id = ?
            AND course_id = ?
            """,
            (
                browser_id,
                course["id"]
            )
        ).fetchone()

        connection.close()

        completed = completed_row["completed"]

        progress = (
            round((completed / total) * 100)
            if total > 0
            else 0
        )

        course_data = dict(course)

        course_data["total"] = total
        course_data["completed"] = completed
        course_data["progress"] = progress

        my_courses_list.append(
            course_data
        )

    response = make_response(
        render_template(
            "my_courses.html",
            courses=my_courses_list
        )
    )

    return set_browser_cookie(
        response,
        browser_id
    )


# =========================================================
# COURSE
# =========================================================

@app.route("/course/<course_id>")
def course(course_id):

    selected_course = None

    for course_item in courses:

        if course_item["id"] == course_id:

            selected_course = course_item
            break

    if selected_course is None:
        return "Course not found", 404

    browser_id = get_browser_id()

    connection = get_db()

    enrollment = connection.execute(
        """
        SELECT 1
        FROM enrollments
        WHERE browser_id = ?
        AND course_id = ?
        """,
        (
            browser_id,
            course_id
        )
    ).fetchone()

    connection.close()

    is_enrolled = enrollment is not None

    tab = request.args.get(
        "tab",
        "overview"
    )

    course_videos = videos.get(
        course_id,
        []
    )

    course_notes = notes.get(
        course_id,
        []
    )

    response = make_response(
        render_template(
            "course.html",
            course=selected_course,
            tab=tab,
            videos=course_videos,
            notes=course_notes,
            is_enrolled=is_enrolled,
            maths_structure=maths_structure,
            maths_notes=maths_notes,
            maths_sheets=maths_sheets,
            maths_overview=maths_overview
        )
    )

    return set_browser_cookie(
        response,
        browser_id
    )


# =========================================================
# ENROLL
# =========================================================

@app.route(
    "/enroll/<course_id>",
    methods=["POST"]
)
def enroll(course_id):

    course_exists = any(
        course["id"] == course_id
        for course in courses
    )

    if not course_exists:
        return "Course not found", 404

    browser_id = get_browser_id()

    connection = get_db()

    connection.execute(
        """
        INSERT OR IGNORE INTO enrollments
        (browser_id, course_id)
        VALUES (?, ?)
        """,
        (
            browser_id,
            course_id
        )
    )

    connection.commit()
    connection.close()

    response = make_response(
        redirect(
            f"/course/{course_id}"
        )
    )

    return set_browser_cookie(
        response,
        browser_id
    )


# =========================================================
# UNENROLL
# =========================================================

@app.route(
    "/unenroll/<course_id>",
    methods=["POST"]
)
def unenroll(course_id):

    browser_id = get_browser_id()

    connection = get_db()

    connection.execute(
        """
        DELETE FROM enrollments
        WHERE browser_id = ?
        AND course_id = ?
        """,
        (
            browser_id,
            course_id
        )
    )

    connection.commit()
    connection.close()

    response = make_response(
        redirect(
            f"/course/{course_id}"
        )
    )

    return set_browser_cookie(
        response,
        browser_id
    )


# =========================================================
# MARK CLASS COMPLETE
# =========================================================

@app.route(
    "/course/<course_id>/video/<int:video_index>/complete",
    methods=["POST"]
)
def complete_video(
    course_id,
    video_index
):

    browser_id = get_browser_id()

    course_videos = videos.get(
        course_id,
        []
    )

    if (
        video_index < 0
        or video_index >= len(course_videos)
    ):
        return "Video not found", 404

    connection = get_db()

    connection.execute(
        """
        INSERT OR IGNORE INTO completed_videos
        (browser_id, course_id, video_index)
        VALUES (?, ?, ?)
        """,
        (
            browser_id,
            course_id,
            video_index
        )
    )

    connection.commit()
    connection.close()

    return "OK"


# =========================================================
# OLD VIDEO ROUTE
# =========================================================

@app.route(
    "/course/<course_id>/video/<int:video_index>"
)
def watch_video(
    course_id,
    video_index
):

    selected_course = None

    for course_item in courses:

        if course_item["id"] == course_id:

            selected_course = course_item
            break

    if selected_course is None:
        return "Course not found", 404

    course_videos = videos.get(
        course_id,
        []
    )

    if (
        video_index < 0
        or video_index >= len(course_videos)
    ):
        return "Video not found", 404

    selected_video = course_videos[
        video_index
    ]

    return render_template(
        "video.html",
        course=selected_course,
        video=selected_video,
        video_index=video_index,
        total_videos=len(course_videos)
    )


# =========================================================
# START
# =========================================================

init_database()


if __name__ == "__main__":
    app.run(
        debug=True
    )