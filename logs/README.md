# Logs Directory

This directory contains all runtime logs and output files generated during testing and development.

## Contents

This directory is used for:
- **Output Files**: Processed X12 EDI JSON output files (`output_*.json`)
- **Response Files**: Lambda invocation response files (`response*.json`)
- **Payload Files**: Test payload files used for Lambda invocations (`payload*.json`)
- **Runtime Logs**: Application logs and debug output

## Git Tracking

The contents of this directory are **excluded from version control** (see `.gitignore`).
Only the `.gitkeep` file is tracked to preserve the directory structure.

## Cleanup

Files in this directory can be safely deleted when no longer needed for debugging or analysis.
The directory will be automatically recreated when running tests or scripts.

## Note

Do not commit any files from this directory to version control. All output and log files
should remain local for debugging purposes only.
