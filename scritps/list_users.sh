#!/bin/bash
cut -d: -f1 /etc/passwd | jq -R . | jq -s .