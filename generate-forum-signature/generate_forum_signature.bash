#!/bin/bash

get_truenas_info() {
    echo "$(midclt call system.info | jq -r '"TrueNAS Version: \(.version)\nCPU Model: \(.model)\nPhysical Memory: \( (.physmem / (1024*1024*1024) *10 | round ) /10 ) GiB \(if .ecc_memory then "(ECC)" else "(Non-ECC)" end)"')"
}

get_motherboard_info() {
    echo "Motherboard: $(dmidecode -t baseboard | grep "Product Name" | awk -F: '{print $2}' | xargs)"
}

get_zfs_pool_info() {
    midclt call pool.query 2>/dev/null | jq -r '
        .[] |
        [
            .name, 
            "\(.topology.data | length) x \(.topology.data[0].type)",
            "\(.topology.data[0].children | length) wide",
            (
                (.size_str | tonumber) |
                if . >= 1099511627776 then 
                    "\((./1099511627776 * 100 + 0.5) | floor / 100) TiB Total"
                else 
                    "\((./1073741824 * 100 + 0.5) | floor / 100) GiB Total"
                end
            ),
            (
                (.free_str | tonumber) |
                if . >= 1099511627776 then 
                    "\((./1099511627776 * 100 + 0.5) | floor / 100) TiB Available"
                else 
                    "\((./1073741824 * 100 + 0.5) | floor / 100) GiB Available"
                end
            ),
            (
                [
                    if (.topology.special | length > 0) then "M" else null end,
                    if (.topology.log | length > 0) then "L" else null end,
                    if (.topology.cache | length > 0) then "C" else null end,
                    if (.topology.spare | length > 0) then "S" else null end,
                    if (.topology.dedup | length > 0) then "D" else null end
                ] | join("")
            )
        ] | join(" | ")
    ' 2>/dev/null |
    awk -F '|' '
        {
            gsub(/\.0 (T|G)iB/, " \\1iB", $4);
            gsub(/\.0 (T|G)iB/, " \\1iB", $5);
            gsub(/[ \t]+\|[ \t]+/, " | ", $0);
            print $0
        }
    ' |
    sed 's/^/Pool: /'
}

echo "Paste the below details into your signature by clicking on your profile picture in the top right and going to Summary -> Preferences -> Profile:"

echo ""
echo "<details>"
echo "<summary>My System</summary>"
echo "<p>"

get_truenas_info | awk -F': ' '{print "<b>" $1 "</b>: " $2 "<br>"}'
get_motherboard_info | awk -F': ' '{print "<b>" $1 "</b>: " $2 "<br>"}'
get_zfs_pool_info | awk -F': ' '{print "<b>" $1 "</b>: " $2 "<br>"}'

echo "</p>"
echo "</details>"