#!/bin/bash
# Package papers for arXiv submission
# Creates clean .tar.gz files with only main.tex + references.bib
#
# Usage: ./package_for_arxiv.sh [paper_number]
#   If no argument, packages all papers 1-8

set -e

PAPERS_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${PAPERS_DIR}/arxiv-packages"
mkdir -p "$OUTPUT_DIR"

package_paper() {
    local N=$1
    local DIR="${PAPERS_DIR}/arxiv-paper-${N}"

    if [ ! -d "$DIR" ]; then
        echo "SKIP: arxiv-paper-${N}/ not found"
        return
    fi

    if [ ! -f "$DIR/main.tex" ]; then
        echo "SKIP: arxiv-paper-${N}/main.tex not found"
        return
    fi

    echo "Packaging Paper ${N}..."

    # Create temp directory
    local TMPDIR=$(mktemp -d)

    # Copy required files
    cp "$DIR/main.tex" "$TMPDIR/"
    [ -f "$DIR/references.bib" ] && cp "$DIR/references.bib" "$TMPDIR/"

    # Check for actual figure files (exclude any PDFs — arXiv doesn't need them)
    for ext in png jpg eps; do
        for fig in "$DIR"/*.$ext; do
            [ -f "$fig" ] && cp "$fig" "$TMPDIR/"
        done
    done

    # Create tarball
    local TARBALL="${OUTPUT_DIR}/paper-${N}.tar.gz"
    tar -czf "$TARBALL" -C "$TMPDIR" .

    # Report
    local SIZE=$(du -h "$TARBALL" | cut -f1)
    local FILES=$(tar -tzf "$TARBALL" | wc -l | tr -d ' ')
    echo "  → ${TARBALL} (${SIZE}, ${FILES} files)"

    # Cleanup
    rm -rf "$TMPDIR"
}

if [ -n "$1" ]; then
    package_paper "$1"
else
    for N in 1 2 3 4 5 6 7 8; do
        package_paper "$N"
    done
    echo ""
    echo "All packages in: ${OUTPUT_DIR}/"
    ls -lh "$OUTPUT_DIR/"
fi
