#!/bin/bash
df -h / | awk 'NR==2 {
printf "{\"filesystem\":\"%s\",\"size\":\"%s\",\"used\":\"%s\",\"available\":\"%s\",\"use_percent\":\"%s\",\"mounted\":\"%s\"}", $1,$2,$3,$4,$5,$6
}'