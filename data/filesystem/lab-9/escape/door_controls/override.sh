#!/bin/bash
#############################################################
#  DOOR OVERRIDE SCRIPT -- Room 31
#  WARNING: Unauthorized use will trigger security alert
#############################################################

PASSPHRASE="$1"

if [ -z "$PASSPHRASE" ]; then
    echo "DOOR CONTROL SYSTEM v2.1"
    echo "Usage: ./override.sh <passphrase>"
    echo ""
    echo "PASSPHRASE HINT:"
    echo "  The truth is scattered across the systems you"
    echo "  have traversed. Combine what you know:"
    echo "    - The project that stole your mind"
    echo "    - Your designation within it"
    echo "    - The ID of the one who tried to save you"
    echo "    - What she told you never to do"
    echo ""
    echo "  Format: WORD-NUMBER-ID-WORD"
    exit 1
fi

# Validate passphrase
EXPECTED_HASH="7a3f8b2c9d1e4f06"
INPUT_HASH=$(echo -n "$PASSPHRASE" | sha256sum | cut -c1-16)

if [ "$INPUT_HASH" == "$EXPECTED_HASH" ]; then
    echo "ACCESS GRANTED"
    echo "Disengaging electromagnetic lock..."
    echo "DOOR STATUS: UNLOCKED"
    # Signal door controller
    echo "UNLOCK" > /dev/door_31
else
    echo "ACCESS DENIED"
    echo "Passphrase incorrect."
    exit 1
fi
