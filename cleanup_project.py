import os
import shutil

# 1. Restore Legacy to pages/
PAGE_DIR = "pages"
BACKUP_DIR = "pages_backup"
ARCHIVE_DIR = "_archive"

# Files to restore (referenced by new menu)
RESTORE_LIST = [
    "legacy_01_daechi_info.py",
    "education.py",
    "ai_matching_reservation.py",
    "chatbot.py", 
    "registration.py",
    "ai_pre_register_legacy.py",
    "shorts.py",
    "youtuber_lab.py",
    "admin.py",
    "sales_system.py",
    "9_MLOps_Dashboard_Admin.py",
    "undervalued.py"
]

if not os.path.exists(PAGE_DIR):
    os.makedirs(PAGE_DIR)

print("--- Restoring legacy files ---")
for f in RESTORE_LIST:
    src = os.path.join(BACKUP_DIR, f)
    dst = os.path.join(PAGE_DIR, f)
    
    if os.path.exists(src):
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"Restored: {f}")
        else:
            print(f"Skipped (exists): {f}")
    else:
        print(f"Warning: Source not found: {f}")

# 2. Reorganize Root Clutter
print("\n--- Cleaning up Root ---")
os.makedirs(ARCHIVE_DIR, exist_ok=True)
os.makedirs(os.path.join(ARCHIVE_DIR, "scripts"), exist_ok=True)
os.makedirs(os.path.join(ARCHIVE_DIR, "docs"), exist_ok=True)
os.makedirs(os.path.join(ARCHIVE_DIR, "large_files"), exist_ok=True)
os.makedirs(os.path.join(ARCHIVE_DIR, "logs"), exist_ok=True)

ROOT_DIR = "."

# Extensions to move
EXT_MAP = {
    ".bat": "scripts",
    ".sh": "scripts",
    ".log": "logs",
    ".txt": "docs", # usually temp txts
    ".md": "docs",  # move mds except core ones
    ".pptx": "large_files",
    ".xlsx": "large_files",
    ".csv": "large_files",
    ".zip": "large_files",
    ".tgz": "large_files",
    ".url": "docs",
}

# Files to KEEP in root
KEEP_FILES = [
    "app.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose-mlops.yml",
    "README.md",
    "README_FINAL.md",
    ".gitignore",
    ".dockerignore",
    "cleanup_project.py" # self
]

# Folders to KEEP in root
KEEP_DIRS = [
    "pages",
    "services",
    "company_docs",
    "data", # keep data folder structure
    "api",
    "mlops",
    "assets",
    ".git",
    ".streamlit",
    "_archive",
    ".venv",
    ".devcontainer",
    ".idea",
    ".vscode"
]

# Move Logic
for item in os.listdir(ROOT_DIR):
    if item in KEEP_FILES or item in KEEP_DIRS:
        continue
    
    src = os.path.join(ROOT_DIR, item)
    
    if os.path.isfile(src):
        ext = os.path.splitext(item)[1].lower()
        if ext in EXT_MAP:
            target_sub = EXT_MAP[ext]
            # Special case: Don't move specific READMEs if critical? 
            # actually moving all other .md to _archive/docs is fine since we have company_docs
            
            # Move
            dst = os.path.join(ARCHIVE_DIR, target_sub, item)
            try:
                shutil.move(src, dst)
                print(f"Moved: {item} -> {target_sub}")
            except Exception as e:
                print(f"Error moving {item}: {e}")
        else:
            # Move other files to _archive root or scripts?
            # Let's move .py scripts in root (except app.py) to scripts
            if ext == ".py":
                dst = os.path.join(ARCHIVE_DIR, "scripts", item)
                try:
                    shutil.move(src, dst)
                    print(f"Moved: {item} -> scripts")
                except Exception as e:
                    print(f"Error moving {item}: {e}")

    elif os.path.isdir(src):
        # Move directories like 'backup', 'deploy', 'pages_backup'
        if item in ["backup", "deploy", "pages_backup", "images", "videos", "outputs"]:
            dst = os.path.join(ARCHIVE_DIR, item)
            try:
                # If dst exists, merge or rename? shutil.move handles directory moves
                if os.path.exists(dst):
                     # renaming if collision
                     dst = os.path.join(ARCHIVE_DIR, item + "_new")
                shutil.move(src, dst)
                print(f"Moved Dir: {item} -> _archive")
            except Exception as e:
                print(f"Error moving dir {item}: {e}")

# 3. Update .gitignore
gitignore_path = ".gitignore"
with open(gitignore_path, "a") as f:
    f.write("\n\n# Cleanup Archive\n_archive/\n")
print("Updated .gitignore")
